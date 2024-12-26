# Google Drive Folder Uploader

Right-click uploader that sends local folders and their contents to Google Drive while preserving structure.

## License
MIT License - Copyright (c) 2024 TayMcQuaya
Credit must be given when using or modifying this code.

## 1. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Google Drive API:
   - Search for "Google Drive API"
   - Click Enable
4. Create OAuth credentials:
   - Go to Credentials page
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop application"
   - Download JSON and rename to `credentials.json`
5. Configure OAuth consent screen:
   - Go to "OAuth consent screen"
   - Select "External"
   - Fill required fields (app name, user support email, developer contact)
   - Add your Google account email under "Test users"
   - Save changes

## 2. Python Setup

1. Install Python requirements:
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. Create project folder structure:
   ```
   G-Drive-Uploader/
   ├── upload_folder.py
   ├── upload_context.bat
   └── credentials.json
   ```

3. Code modifications needed:
   - In `upload_folder.py`: Update SCRIPT_DIR path:
     ```python
     SCRIPT_DIR = "C:/Your/Path/To/G-Drive-Uploader"  # Update this
     ```

   - In `upload_context.bat`: Update Python script path:
     ```batch
     @echo off
     python "C:\Your\Path\To\G-Drive-Uploader\upload_folder.py" %*
     pause
     ```

## 3. Windows Registry Setup

1. Open Registry Editor (regedit)
2. Navigate to: `HKEY_CLASSES_ROOT\Directory\shell`
3. Create new key:
   - Right click → New → Key
   - Name it: `UploadToGDrive`
   - Set default value to: `Upload to Google Drive`

4. Create command subkey:
   - Under `UploadToGDrive`, create new key named `command`
   - Set default value to: `"C:\Your\Path\To\G-Drive-Uploader\upload_context.bat" "%1"`

## 4. First-Time Usage

1. Right-click any folder
2. Select "Upload to Google Drive"
3. Browser opens for Google authorization
4. Allow access
5. `token.json` generates in script directory

## 5. Regular Usage

1. Right-click any folder you want to upload
2. Select "Upload to Google Drive" from context menu
3. Files and subfolders upload automatically to your Google Drive
4. Structure is preserved - folders and subfolders appear the same way in Google Drive
5. Existing files are automatically replaced if they have the same name

## Troubleshooting

- If `token.json` is deleted: Re-authorize through browser
- If credentials expire: Delete `token.json` and re-authorize
- Path issues: Ensure all paths in code use correct format:
  - Python: Use forward slashes or double backslashes
  - Batch: Use backslashes
  - Registry: Use double backslashes