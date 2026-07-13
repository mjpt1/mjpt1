#!/usr/bin/env python3
"""Update README.md Latest Projects section from newest public repos."""

from __future__ import annotations

import json
import os
import re
import urllib.request

USERNAME = os.environ.get("GITHUB_REPOSITORY_OWNER", "mjpt1")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
COUNT = int(os.environ.get("LATEST_PROJECTS_COUNT", "6"))
README_PATH = os.environ.get("README_PATH", "README.md")
START = "<!-- LATEST_PROJECTS:START -->"
END = "<!-- LATEST_PROJECTS:END -->"

LANG_EMOJI = {
    "TypeScript": "🟦",
    "JavaScript": "🟨",
    "Python": "🐍",
    "HTML": "🌐",
    "CSS": "🎨",
    "Java": "☕",
    "Kotlin": "📱",
    "Go": "🐹",
    "Rust": "🦀",
    "PHP": "🐘",
    "C#": "💜",
    "C++": "⚙️",
    "Ruby": "💎",
    "Dart": "🎯",
    "Swift": "🍎",
}


def api_get(url: str) -> list | dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mjpt1-profile-readme",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def fetch_latest_repos() -> list[dict]:
    repos = api_get(
        f"https://api.github.com/users/{USERNAME}/repos"
        f"?sort=updated&direction=desc&per_page=40&type=owner"
    )
    selected = []
    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        if repo.get("name") == USERNAME:
            continue
        selected.append(repo)
        if len(selected) >= COUNT:
            break
    return selected


def escape_md(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def render_cell(repo: dict) -> str:
    name = repo["name"]
    url = repo["html_url"]
    lang = repo.get("language") or "Project"
    emoji = LANG_EMOJI.get(lang, "📦")
    desc = escape_md(repo.get("description") or "Recently updated repository.")
    homepage = (repo.get("homepage") or "").strip()

    lines = [
        f"### {emoji} [{name}]({url})",
        f"**{desc}**",
        "",
        f"[![Repo](https://img.shields.io/badge/Repository-7c3aed?style=for-the-badge&logo=github&logoColor=white)]({url})",
    ]
    if homepage:
        lines.append(
            f"[![Live](https://img.shields.io/badge/Live%20Demo-ef4444?style=for-the-badge&logo=vercel&logoColor=white)]({homepage})"
        )
    lines.append("")
    lines.append(f"`{lang}`")
    return "\n".join(lines)


def render_section(repos: list[dict]) -> str:
    rows = []
    for i in range(0, len(repos), 2):
        left = render_cell(repos[i])
        right = render_cell(repos[i + 1]) if i + 1 < len(repos) else ""
        rows.append(
            "<tr>\n"
            f'<td width="50%">\n\n{left}\n\n</td>\n'
            f'<td width="50%">\n\n{right}\n\n</td>\n'
            "</tr>"
        )

    body = "\n".join(rows)
    return (
        f"{START}\n"
        "## 🚀 Latest Projects\n\n"
        "Recently updated repositories — refreshed automatically.\n\n"
        f"<table>\n{body}\n</table>\n"
        f"{END}"
    )


def main() -> None:
    repos = fetch_latest_repos()
    if not repos:
        raise SystemExit("No repositories found to render.")

    section = render_section(repos)
    with open(README_PATH, encoding="utf-8") as f:
        readme = f.read()

    pattern = re.compile(
        re.escape(START) + r"[\s\S]*?" + re.escape(END),
        re.MULTILINE,
    )
    if not pattern.search(readme):
        raise SystemExit("LATEST_PROJECTS markers not found in README.md")

    updated = pattern.sub(section, readme)
    with open(README_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(updated)

    print(f"Updated {len(repos)} latest projects:")
    for repo in repos:
        print(f" - {repo['name']} ({repo.get('updated_at')})")


if __name__ == "__main__":
    main()
