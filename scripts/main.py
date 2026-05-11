"""Main entry point. Walks Drive source, converts changed files, writes output locally."""
import argparse
import json
import logging
import shutil
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import config
from utils import drive, manifest as mf, index as idx
from converters import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("kb-sync")


def process_one(service, file_meta, manifest):
    """Download, convert, save locally, update manifest. Returns (file_id, success_bool)."""
    fid = file_meta["id"]
    name = file_meta["name"]
    mime_type = file_meta.get("mimeType", "")

    # Google Workspace files have no extension — map by mimeType to export format
    if mime_type in config.GOOGLE_WORKSPACE_MIME:
        ext = config.GOOGLE_WORKSPACE_MIME[mime_type]
    else:
        ext = Path(name).suffix.lower()

    if ext not in config.ALL_SUPPORTED:
        log.info(f"SKIP unsupported: {name}")
        return fid, False

    output_name = idx.safe_output_name(file_meta)
    local_path = config.WORK_DIR / fid / (Path(name).stem + ext)

    try:
        log.info(f"DOWNLOAD {file_meta['path']}")
        drive.download_file(service, fid, local_path, mime_type)

        log.info(f"CONVERT {name}")
        result, converter = router.route_and_convert(str(local_path))

        if result is router.PASSTHROUGH:
            # .txt → .md, .md → .md (content copied as-is, no LLM)
            out_ext = ".md" if ext == ".txt" else ext
            output_name = output_name.rsplit(".", 1)[0] + out_ext
            dest = config.OUTPUT_DIR / output_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_path, dest)
        else:
            md = idx.build_frontmatter(file_meta, converter) + result
            dest = config.OUTPUT_DIR / output_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(md, encoding="utf-8")

        mf.update_entry(manifest, file_meta, output_name, status="ok")
        log.info(f"DONE {output_name}")
        return fid, True
    except Exception as e:
        log.error(f"FAIL {name}: {e}")
        mf.update_entry(manifest, file_meta, output_name, status="error", error=str(e))
        return fid, False
    finally:
        try:
            if local_path.exists():
                local_path.unlink()
            if local_path.parent.exists():
                local_path.parent.rmdir()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None,
                        help="Process at most N files (for testing)")
    parser.add_argument("--status", action="store_true",
                        help="Show sync diff between Drive and local wiki, then exit")
    parser.add_argument("--type", choices=["doc", "image", "audio", "video"],
                        help="Filter to files of this type only (forces re-queue of skipped entries)")
    parser.add_argument("--file", metavar="PATTERN",
                        help="Filter to files whose name contains PATTERN (case-insensitive, forces re-queue)")
    args = parser.parse_args()

    if not config.GEMINI_API_KEY:
        raise SystemExit("Set GEMINI_API_KEY env var")

    config.WORK_DIR.mkdir(parents=True, exist_ok=True)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_path = config.OUTPUT_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    log.info(f"Manifest has {len(manifest)} entries")

    # Migrate: strip spaces from path components in existing manifest entries + rename on disk
    def _clean_path(p):
        return "/".join(s.strip() for s in p.split("/")) if p else p

    for entry in manifest.values():
        old_name = entry.get("output_name", "")
        new_name = _clean_path(old_name)
        if old_name and old_name != new_name:
            old_file = config.OUTPUT_DIR / old_name
            new_file = config.OUTPUT_DIR / new_name
            if old_file.exists():
                new_file.parent.mkdir(parents=True, exist_ok=True)
                old_file.rename(new_file)
                log.info(f"RENAME {old_name} -> {new_name}")
            entry["output_name"] = new_name
        if entry.get("path"):
            entry["path"] = _clean_path(entry["path"])

    # Migrate: rename .txt output files → .md on disk and in manifest
    for entry in manifest.values():
        old_name = entry.get("output_name", "")
        if old_name.endswith(".txt"):
            new_name = old_name[:-4] + ".md"
            old_file = config.OUTPUT_DIR / old_name
            new_file = config.OUTPUT_DIR / new_name
            if old_file.exists():
                new_file.parent.mkdir(parents=True, exist_ok=True)
                old_file.rename(new_file)
                log.info(f"RENAME {old_name} -> {new_name}")
            entry["output_name"] = new_name

    service = drive.get_service()
    log.info("Listing source files...")
    all_files = list(drive.list_files_recursive(service, config.SOURCE_FOLDER_ID))
    log.info(f"Found {len(all_files)} files in source")

    # Sync manifest with reality
    drive_ids = {f["id"] for f in all_files}
    purged = []
    force_reprocess = set()
    for fid in list(manifest.keys()):
        entry = manifest[fid]
        if fid not in drive_ids:
            # Source deleted from Drive — purge manifest + index
            manifest.pop(fid)
            purged.append(entry.get("path") or entry["name"])
            log.info(f"PURGE (deleted from Drive): {entry['name']}")
        elif not (config.OUTPUT_DIR / entry["output_name"]).exists():
            # Local file missing — reprocess from Drive
            force_reprocess.add(fid)
            log.info(f"REPROCESS (missing locally): {entry['name']}")

    _type_exts = {
        "doc":   config.DOC_EXTS | config.TEXT_EXTS | config.PDF_EXTS | config.SPREADSHEET_EXTS | config.PRESENTATION_EXTS,
        "image": config.IMAGE_EXTS,
        "audio": config.AUDIO_EXTS,
        "video": config.VIDEO_EXTS,
    }

    def _file_ext(f):
        mime = f.get("mimeType", "")
        return config.GOOGLE_WORKSPACE_MIME.get(mime) or Path(f["name"]).suffix.lower()

    def _priority(f):
        ext = _file_ext(f)
        for rank, exts in enumerate(_type_exts.values()):
            if ext in exts:
                return rank
        return len(_type_exts)

    # Force-requeue files previously marked skipped if their type is now active
    if args.type:
        target_exts = _type_exts[args.type]
        for f in all_files:
            if _file_ext(f) in target_exts:
                entry = manifest.get(f["id"], {})
                if entry.get("status") == "skipped":
                    force_reprocess.add(f["id"])

    if args.file:
        pattern = args.file.lower()
        for f in all_files:
            if pattern in f["name"].lower():
                force_reprocess.add(f["id"])

    def _matches_filter(f):
        if args.file:
            return args.file.lower() in f["name"].lower()
        if args.type:
            return _file_ext(f) in _type_exts[args.type]
        return True

    pending = sorted(
        [f for f in all_files
         if _matches_filter(f) and (mf.needs_conversion(manifest, f) or f["id"] in force_reprocess)],
        key=_priority,
    )
    if args.limit:
        pending = pending[: args.limit]
        log.info(f"--limit {args.limit}: processing {len(pending)} file(s)")
    else:
        log.info(f"{len(pending)} files need conversion")

    if args.status:
        print("\n=== SYNC STATUS: Drive vs Wiki ===\n")
        if pending:
            print(f"TO ADD ({len(pending)} files):")
            for f in pending:
                print(f"  + {f['path']}")
        if purged:
            print(f"\nTO REMOVE ({len(purged)} files):")
            for path in purged:
                print(f"  - {path}")
        synced = len(all_files) - len(pending)
        print(f"\nALREADY SYNCED: {synced} file(s)")
        print("\nRun without --status to apply.\n")
        return

    # Delete local files not tracked in manifest (full sync only — skip when filtering)
    if not args.file and not args.type:
        tracked = {entry["output_name"] for entry in manifest.values()}
        for f in config.OUTPUT_DIR.rglob("*"):
            if f.is_file() and f.name not in {"manifest.json", "_INDEX.md"} and not f.name.startswith("."):
                rel = f.relative_to(config.OUTPUT_DIR).as_posix()
                if rel not in tracked:
                    f.unlink()
                    log.info(f"DELETE (not in manifest): {rel}")
        # Remove empty dirs left behind
        for d in sorted(config.OUTPUT_DIR.rglob("*"), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()

    if not pending:
        log.info("Nothing to process — updating index.")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (config.OUTPUT_DIR / "_INDEX.md").write_text(idx.build_index(config.OUTPUT_DIR), encoding="utf-8")
        return

    completed = 0

    try:
        with ThreadPoolExecutor(max_workers=config.MAX_PARALLEL) as pool:
            active = {pool.submit(process_one, service, f, manifest): f for f in pending}
            while active:
                done, _ = concurrent.futures.wait(active, timeout=0.5,
                                                   return_when=concurrent.futures.FIRST_COMPLETED)
                for fut in done:
                    del active[fut]
                    fut.result()
                    completed += 1
                    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
                    log.info(f"Progress: {completed}/{len(pending)}")
    except KeyboardInterrupt:
        log.info("Interrupted — progress saved to manifest.")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        raise SystemExit(1)

    log.info("Final save: manifest + index")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (config.OUTPUT_DIR / "_INDEX.md").write_text(idx.build_index(config.OUTPUT_DIR), encoding="utf-8")
    log.info(f"Done. Output in: {config.OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
