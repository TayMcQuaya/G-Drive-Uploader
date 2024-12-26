import os
import sys

from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials  # Not used by default, but here just for reference
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where upload_folder.py is
TOKEN_PATH = os.path.join(SCRIPT_DIR, 'token.json')  # path to token.json

# If modifying these scopes, delete the token.json file to re-authenticate.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_drive_api():
    creds_path = os.getenv("GDRIVE_CREDENTIALS_PATH", "credentials.json")
    
    if not os.path.isfile(creds_path):
        raise FileNotFoundError(
            f"Could not find credentials file at '{creds_path}'. "
            "Please set GDRIVE_CREDENTIALS_PATH to the correct path."
        )
    
    creds = None
    
    if os.path.exists(TOKEN_PATH):  # Using TOKEN_PATH constant
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, 'w') as token:  # Using TOKEN_PATH constant
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def find_or_create_drive_folder(drive_service, folder_name, parent_id=None):
    """
    Finds a folder named `folder_name` in Google Drive under parent_id, if specified.
    If not found, creates it. Returns the folder ID.
    """
    query_parts = [
        f"name = '{folder_name}'",
        "mimeType = 'application/vnd.google-apps.folder'",
        "trashed = false"
    ]
    if parent_id:
        query_parts.append(f"'{parent_id}' in parents")

    query = " and ".join(query_parts)

    response = drive_service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    items = response.get('files', [])
    if items:
        # Folder exists; return the first match
        return items[0]['id']
    else:
        # Create the folder
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            metadata['parents'] = [parent_id]

        folder = drive_service.files().create(body=metadata, fields='id').execute()
        return folder.get('id')

def upload_or_replace_file(drive_service, folder_id, filepath):
    """
    Uploads a file into Google Drive folder_id. 
    If the file (by name) already exists in that folder, it's replaced.
    """
    filename = os.path.basename(filepath)

    # Search for file with this name in the specified folder
    query_parts = [
        f"name = '{filename}'",
        "trashed = false",
        f"'{folder_id}' in parents"
    ]
    query = " and ".join(query_parts)
    existing_files = drive_service.files().list(
        q=query, spaces='drive', fields='files(id, name)'
    ).execute().get('files', [])

    media_body = MediaFileUpload(filepath, resumable=True)

    if existing_files:
        # Update the existing file
        file_id = existing_files[0]['id']
        drive_service.files().update(
            fileId=file_id,
            media_body=media_body
        ).execute()
        print(f"Updated: {filename} (File ID: {file_id})")
    else:
        # Upload as new file
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        new_file = drive_service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields='id'
        ).execute()
        print(f"Uploaded: {filename} (File ID: {new_file.get('id')})")

def upload_folder_to_drive(local_folder_path):
    """
    Main function to upload a folder (and subfolders/files) to Google Drive.
    """
    drive_service = authenticate_drive_api()

    # Create/find a top-level folder with the same name as the local folder
    top_level_folder_name = os.path.basename(os.path.normpath(local_folder_path))
    top_level_folder_id = find_or_create_drive_folder(drive_service, top_level_folder_name)

    # Walk the folder tree
    for root, dirs, files in os.walk(local_folder_path):
        # "root" is the current directory path, relative to the top-level folder
        # We need to replicate this structure in Drive
        relative_path = os.path.relpath(root, local_folder_path)
        path_parts = relative_path.split(os.sep)

        current_drive_folder_id = top_level_folder_id
        for part in path_parts:
            # If "relative_path" is '.', it means we're at the top-level folder
            if part == '.':
                continue
            # Otherwise, find/create subfolder
            current_drive_folder_id = find_or_create_drive_folder(
                drive_service, part, current_drive_folder_id
            )

        # Upload all files in the current directory
        for file_name in files:
            file_path = os.path.join(root, file_name)
            upload_or_replace_file(drive_service, current_drive_folder_id, file_path)

    print("\nAll files uploaded/replaced successfully!")

def main():
    folder_path = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else os.getcwd()
    folder_path = folder_path.strip('"').strip("'")

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        sys.exit(1)

    print(f"Uploading files from: {folder_path}")
    upload_folder_to_drive(folder_path)

if __name__ == "__main__":
    main()
