from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tempfile
import json
from io import BytesIO

def upload_to_drive(file_buffer: BytesIO, filename: str, folder_id: str, credentials_path: str) -> str:
    try:
        # Save credentials to a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_creds:
            temp_creds.write(credentials_path if credentials_path.strip().startswith('{') else open(credentials_path).read())
            temp_creds.flush()

            gauth = GoogleAuth()
            gauth.LoadCredentialsFile(temp_creds.name)

            if gauth.credentials is None:
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                gauth.Refresh()
            else:
                gauth.Authorize()

            gauth.SaveCredentialsFile(temp_creds.name)

        drive = GoogleDrive(gauth)

        file_drive = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
        file_buffer.seek(0)
        file_drive.SetContentString(file_buffer.read().decode('latin1'))  # Use decode to handle binary buffer
        file_drive.Upload()

        return f"https://drive.google.com/file/d/{file_drive['id']}/view"

    except Exception as e:
        return f"Google Drive upload failed: {str(e)}"
