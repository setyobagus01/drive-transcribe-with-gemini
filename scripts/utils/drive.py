"""Google Drive client - list files and download."""
from pathlib import Path
from google.auth.credentials import AnonymousCredentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import config

SCOPES = ["https://www.googleapis.com/auth/drive"]

GOOGLE_WORKSPACE_EXPORT = {
    "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.google-apps.presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def get_service():
    if config.SERVICE_ACCOUNT_FILE and Path(config.SERVICE_ACCOUNT_FILE).exists():
        creds = service_account.Credentials.from_service_account_file(
            config.SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    else:
        creds = AnonymousCredentials()
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def list_files_recursive(service, folder_id):
    """Yield all files under folder_id recursively. Returns dicts with id, name, mimeType, modifiedTime, md5Checksum, parents, path."""
    def walk(fid, prefix=""):
        page_token = None
        while True:
            resp = service.files().list(
                q=f"'{fid}' in parents and trashed=false",
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, md5Checksum, size)",
                pageSize=1000,
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()
            for f in resp.get("files", []):
                f["path"] = f"{prefix}/{f['name']}" if prefix else f["name"]
                if f["mimeType"] == "application/vnd.google-apps.folder":
                    yield from walk(f["id"], f["path"])
                else:
                    yield f
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    yield from walk(folder_id)


def download_file(service, file_id, dest_path, mime_type=None):
    """Download file to dest_path. Uses export_media for Google Workspace types."""
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    export_mime = GOOGLE_WORKSPACE_EXPORT.get(mime_type)
    if export_mime:
        request = service.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        request = service.files().get_media(fileId=file_id)
    with open(dest_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()


