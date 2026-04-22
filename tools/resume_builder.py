#!/usr/bin/env python3
"""Generate a role-tailored resume draft from structured JSON input.

The tool enforces formatting/content rules intended to maximize interview
conversion for a specific target role.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL_FIELDS = [
    "target_role_or_jd",
    "experience_summary",
    "career_level",
    "special_context",
]


@dataclass
class ResumeBuilder:
    data: dict[str, Any]

    def missing_required_context(self) -> list[str]:
        missing: list[str] = []
        for key in REQUIRED_TOP_LEVEL_FIELDS:
            value = self.data.get(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(key)
        return missing

    def render(self) -> str:
        sections: list[str] = []
        sections.append(self._render_header())

        if self._should_include_summary():
            sections.append(self._render_summary())

        sections.append(self._render_experience())
        sections.append(self._render_languages_and_technologies())
        sections.append(self._render_projects())
        sections.append(self._render_education())
        sections.append(self._render_extracurricular())
        sections.append(self._render_interests())

        sections.append(self._render_missing_info_flags())
        sections.append(self._render_changes_made())
        return "\n\n".join([section for section in sections if section.strip()])

    def _render_header(self) -> str:
        profile = self.data.get("profile", {})
        name = profile.get("name", "Candidate Name")
        location = profile.get("location", "City, State")
        email = profile.get("email", "email@example.com")
        phone = profile.get("phone", "(555) 555-5555")
        links = profile.get("links", [])

        link_chunks = []
        for item in links:
            label = item.get("label", "Link")
            url = item.get("url", "")
            if url:
                link_chunks.append(f"[{label}]({url})")

        contact_line = " | ".join(
            [value for value in [location, phone, email] if value]
            + link_chunks
        )

        return f"# {name}\n\n{contact_line}"

    def _should_include_summary(self) -> bool:
        level = str(self.data.get("career_level", "")).lower()
        years = self.data.get("years_experience", 0)
        special_context = str(self.data.get("special_context", "")).lower()

        senior_levels = {"senior", "tech lead", "engineering manager"}
        return (
            level in senior_levels
            or years >= 5
            or any(
                token in special_context
                for token in ["career change", "career break", "returning", "switching tracks"]
            )
        )

    def _render_summary(self) -> str:
        summary = self.data.get("summary", "").strip()
        if not summary:
            return (
                "## Summary\n"
                "Tailored summary needed (2–4 sentences): include years of experience, "
                "most relevant domain strengths, and impact aligned to the target role."
            )
        return f"## Summary\n{summary}"

    def _render_experience(self) -> str:
        experience = self.data.get("experience", [])
        if not experience:
            return "## Work Experience\n- Add role history in reverse chronological order."

        lines = ["## Work Experience"]
        for role in experience:
            title = role.get("title", "Title")
            company = role.get("company", "Company")
            start = role.get("start", "Year")
            end = role.get("end", "Present")
            location = role.get("location", "")
            tech = role.get("technologies", [])

            lines.append(f"**{title}**, **{company}** | **{start} – {end}**")
            if location:
                lines.append(location)
            if tech:
                lines.append(f"Technologies: {', '.join(tech)}")

            bullets = role.get("bullets", [])
            if bullets:
                for bullet in bullets:
                    lines.append(f"* {bullet}")
            else:
                lines.append(
                    "* Accomplished [impact] as measured by [number] by doing [specific contribution] using [technologies]."
                )

        return "\n".join(lines)

    def _render_languages_and_technologies(self) -> str:
        skills = self.data.get("languages_and_technologies", {})
        langs = skills.get("languages", [])
        frameworks = skills.get("frameworks", [])
        platforms = skills.get("platforms", [])
        tools = skills.get("tools", [])

        lines = ["## Languages & Technologies"]
        if langs:
            lines.append(f"**Languages:** {', '.join(langs)}")
        if frameworks:
            lines.append(f"**Frameworks/Libraries:** {', '.join(frameworks)}")
        if platforms:
            lines.append(f"**Cloud/Platforms:** {', '.join(platforms)}")
        if tools:
            lines.append(f"**Developer Tooling:** {', '.join(tools)}")

        if len(lines) == 1:
            lines.append("Add only currently hands-on technologies aligned with the target JD.")

        return "\n".join(lines)

    def _render_projects(self) -> str:
        projects = self.data.get("projects", [])
        if not projects:
            return ""

        lines = ["## Projects"]
        for project in projects:
            name = project.get("name", "Project")
            link = project.get("link", "")
            date = project.get("date", "")
            tech = ", ".join(project.get("technologies", []))

            header = f"**{name}**"
            if link:
                header = f"[{name}]({link})"
            if date:
                header += f" | **{date}**"
            lines.append(header)

            if tech:
                lines.append(f"Technologies: {tech}")

            for bullet in project.get("bullets", []):
                lines.append(f"* {bullet}")

        return "\n".join(lines)

    def _render_education(self) -> str:
        education = self.data.get("education", [])
        if not education:
            return ""

        lines = ["## Education"]
        for item in education:
            degree = item.get("degree", "Degree")
            school = item.get("school", "School")
            year = item.get("year", "Year")
            gpa = item.get("gpa", "")
            parts = [f"**{degree}**, **{school}**", f"**{year}**"]
            if gpa:
                parts.append(f"GPA: {gpa}")
            lines.append(" | ".join(parts))

        return "\n".join(lines)

    def _render_extracurricular(self) -> str:
        items = self.data.get("extracurricular", [])
        if not items:
            return ""

        lines = ["## Extracurricular / Open Source / Publications"]
        for item in items:
            lines.append(f"* {item}")
        return "\n".join(lines)

    def _render_interests(self) -> str:
        interests = self.data.get("interests", [])
        if not interests:
            return ""

        return "## Interests\n" + ", ".join(interests)

    def _render_missing_info_flags(self) -> str:
        flags: list[str] = []
        missing_required = self.missing_required_context()
        if missing_required:
            flags.append(
                "Missing required setup inputs: " + ", ".join(missing_required)
            )

        for role in self.data.get("experience", []):
            for bullet in role.get("bullets", []):
                if not any(ch.isdigit() for ch in bullet):
                    flags.append(
                        f"Bullet under {role.get('company', 'company')} has no metric: '{bullet}'"
                    )

        if not self.data.get("target_role_or_jd"):
            flags.append(
                "No job description provided. Tailoring to a specific JD significantly improves interview conversion."
            )

        if not flags:
            return ""

        lines = ["## Information needed to improve this draft"]
        for flag in flags:
            lines.append(f"* {flag}")
        return "\n".join(lines)

    def _render_changes_made(self) -> str:
        return (
            "## Changes made\n"
            "* Reorganized content to prioritize interview-relevant scanning order (impact, skills, chronology).\n"
            "* Enforced metric-driven bullet style and highlighted missing quantification where needed.\n"
            "* Applied one-column, reverse-chronological, ATS-friendly markdown structure ready for PDF export."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a role-tailored resume draft from structured JSON input. "
            "Output is markdown that can be converted to PDF."
        )
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file.")
    parser.add_argument(
        "--output",
        default="-",
        help="Output markdown path. Use '-' for stdout (default).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    data = json.loads(input_path.read_text(encoding="utf-8"))

    builder = ResumeBuilder(data=data)
    output = builder.render()

    if args.output == "-":
        print(output)
    else:
        Path(args.output).write_text(output + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
