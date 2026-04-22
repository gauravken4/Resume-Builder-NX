# Install the Resume Builder on a WordPress + Elementor Site

This project is a Python CLI (`tools/resume_builder.py`), so WordPress cannot run it directly inside Elementor by itself.
The reliable production setup is:

1. Host the Python tool behind an HTTP API.
2. Submit candidate data from an Elementor form.
3. Call your API (via webhook/plugin code).
4. Return the generated markdown (or PDF) to the user.

## Architecture

- **Frontend:** WordPress + Elementor form/page.
- **Backend:** Python API service that executes `resume_builder.py` logic.
- **Optional:** Convert markdown to PDF before returning download link.

## Step 1: Deploy the Python service

On a VPS/container (Ubuntu example):

```bash
sudo apt update
sudo apt install -y python3 python3-venv nginx

mkdir -p /opt/resume-builder
cd /opt/resume-builder
# copy project files here (at least tools/resume_builder.py)

python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn
```

Create `api.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

from tools.resume_builder import ResumeBuilder

app = FastAPI()


class ResumePayload(BaseModel):
    data: dict[str, Any]


@app.post("/build-resume")
def build_resume(payload: ResumePayload):
    builder = ResumeBuilder(data=payload.data)
    md = builder.render()
    return {"resume_markdown": md, "missing": builder.missing_required_context()}
```

Run API:

```bash
uvicorn api:app --host 0.0.0.0 --port 8080
```

Put Nginx + SSL (Let's Encrypt) in front, then expose:

- `https://your-api-domain.com/build-resume`

## Step 2: Build the Elementor form

In Elementor:

1. Add a **Form** widget.
2. Add fields mapping to your JSON model, for example:
   - `target_role_or_jd`
   - `experience_summary`
   - `career_level`
   - `special_context`
   - experience/project fields you need
3. In **Actions After Submit**, include **Webhook**.
4. Set webhook URL to your WordPress endpoint (next step) or directly to API if you already transform form fields to JSON.

## Step 3: Add a tiny WordPress bridge endpoint

Elementor sends URL-encoded form payloads; your Python API expects structured JSON.
Use a mini plugin bridge to transform and forward data.

Create `wp-content/plugins/resume-builder-bridge/resume-builder-bridge.php`:

```php
<?php
/**
 * Plugin Name: Resume Builder Bridge
 */

add_action('rest_api_init', function () {
    register_rest_route('resume-builder/v1', '/submit', [
        'methods'  => 'POST',
        'callback' => 'rb_submit',
        'permission_callback' => '__return_true',
    ]);
});

function rb_submit(WP_REST_Request $request) {
    $p = $request->get_params();

    $data = [
        'target_role_or_jd' => sanitize_text_field($p['target_role_or_jd'] ?? ''),
        'experience_summary' => sanitize_textarea_field($p['experience_summary'] ?? ''),
        'career_level' => sanitize_text_field($p['career_level'] ?? ''),
        'special_context' => sanitize_text_field($p['special_context'] ?? ''),
        'profile' => [
            'name' => sanitize_text_field($p['name'] ?? ''),
            'email' => sanitize_email($p['email'] ?? ''),
        ],
    ];

    $response = wp_remote_post('https://your-api-domain.com/build-resume', [
        'timeout' => 20,
        'headers' => ['Content-Type' => 'application/json'],
        'body'    => wp_json_encode(['data' => $data]),
    ]);

    if (is_wp_error($response)) {
        return new WP_REST_Response(['error' => $response->get_error_message()], 500);
    }

    $body = json_decode(wp_remote_retrieve_body($response), true);
    return new WP_REST_Response($body, 200);
}
```

Activate plugin in **WP Admin → Plugins**.

Set Elementor webhook URL to:

- `https://your-site.com/wp-json/resume-builder/v1/submit`

## Step 4: Show result to user

Two common patterns:

- **Email result:** Email generated markdown/PDF link after submission.
- **Results page:** Store API response in DB/session and redirect to a page that renders the result.

For quick MVP, return JSON and use automation (Zapier/Make/custom JS) to email/download.

## Step 5: Security and production hardening

- Add API key header from WordPress to Python API.
- Enable rate limiting on Nginx/Cloudflare.
- Validate required fields before forwarding.
- Log requests without storing sensitive PII longer than needed.
- Add CAPTCHA to Elementor form.

## Important constraints

- Keep generated resume output as markdown/plain text, then convert to **PDF** before delivery.
- Never fabricate achievements or metrics.
- Tailor each submission to a specific job description for best results.

## Local smoke test

```bash
python3 tools/resume_builder.py --input examples/resume_input_template.json --output /tmp/resume.md
```

If this command succeeds, your resume generation engine is working.
