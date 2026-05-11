"""Manifest = state file tracking which files have been converted and their checksums."""

def needs_conversion(manifest, file_meta):
    """Return True if file is new or changed since last sync."""
    entry = manifest.get(file_meta["id"])
    if not entry:
        return True
    # md5Checksum is reliable for binary files; modifiedTime as fallback
    if file_meta.get("md5Checksum"):
        return entry.get("md5") != file_meta["md5Checksum"]
    return entry.get("modifiedTime") != file_meta.get("modifiedTime")


def update_entry(manifest, file_meta, output_name, status="ok", error=None):
    manifest[file_meta["id"]] = {
        "name": file_meta["name"],
        "path": file_meta.get("path"),
        "md5": file_meta.get("md5Checksum"),
        "modifiedTime": file_meta.get("modifiedTime"),
        "output_name": output_name,
        "status": status,
        "error": error,
    }
