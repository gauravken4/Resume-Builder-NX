import os
from typing import Dict, Any, List
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ResumeBuilder:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def missing_required_context(self) -> List[str]:
        required = ["target_role_or_jd", "experience_summary"]
        return [key for key in required if not self.data.get(key)]

    def render(self) -> str:
        prompt = f"""
You are a professional resume writer.

Create an ATS-optimized resume using this data:

Target Role: {self.data.get("target_role_or_jd")}
Experience Summary: {self.data.get("experience_summary")}

Instructions:
- Use strong action verbs
- Add measurable impact (numbers, %)
- Use bullet points
- Keep it clean markdown
- Make it ATS-friendly
- Keep it concise but powerful

Return ONLY the resume.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content
