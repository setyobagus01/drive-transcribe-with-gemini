"""Generate _INDEX.md by scanning the output directory."""
import re
from collections import defaultdict
from pathlib import Path

SKIP_FILES = {"_INDEX.md", "manifest.json"}

# Characters illegal in Windows filenames
_WIN_ILLEGAL = re.compile(r'[\\/:*?"<>|\x00-\x1f�]')


def _sanitize_part(part):
    """Remove Windows-illegal chars and strip whitespace from a single path component."""
    return _WIN_ILLEGAL.sub("", part).strip()


def build_index(output_dir):
    """Scan output_dir and return markdown string for _INDEX.md."""
    output_dir = Path(output_dir)

    all_files = sorted([
        f.relative_to(output_dir).as_posix()
        for f in output_dir.rglob("*")
        if f.is_file() and f.name not in SKIP_FILES and not f.name.startswith(".")
    ])

    lines = ["# Knowledge Base Index", ""]
    lines.append(f"_Total: {len(all_files)} file(s)_\n")

    groups = defaultdict(list)
    for path in all_files:
        top = path.split("/")[0] if "/" in path else "(root)"
        groups[top].append(path)

    for top in sorted(groups):
        lines.append(f"## {top}\n")
        for path in sorted(groups[top]):
            stem = Path(path).stem
            lines.append(f"- [[{path}|{stem}]]")
        lines.append("")

    return "\n".join(lines)


def build_frontmatter(file_meta, converter):
    """YAML frontmatter prepended to each .md file."""
    return (
        "---\n"
        f"source: {file_meta.get('path') or file_meta['name']}\n"
        f"source_id: {file_meta['id']}\n"
        f"modified: {file_meta.get('modifiedTime', '')}\n"
        f"converter: {converter}\n"
        "---\n\n"
    )


def safe_output_name(file_meta):
    """Convert source path to .md filename preserving folder structure."""
    path = (file_meta.get("path") or file_meta["name"]).replace("\\", "/")
    # Sanitize each component: strip spaces + remove Windows-illegal chars
    parts = [_sanitize_part(p) for p in path.split("/")]
    path = "/".join(p for p in parts if p)  # drop any empty parts
    stem = path.rsplit(".", 1)[0] if "." in path.split("/")[-1] else path
    return f"{stem}.md"
