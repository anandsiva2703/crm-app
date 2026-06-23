import streamlit as st
import pandas as pd
import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests
import config
import os
import tempfile

def get_oauth_creds():
    if "oauth_creds" not in st.session_state or not st.session_state.oauth_creds:
        return None
    creds_dict = st.session_state.oauth_creds
    creds = Credentials(
        token=creds_dict.get("token"),
        refresh_token=creds_dict.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        st.session_state.oauth_creds["token"] = creds.token
    return creds

def get_sheet_client():
    creds = get_oauth_creds()
    if not creds:
        return None
    return gspread.authorize(creds)

def get_worksheet(sheet_name):
    client = get_sheet_client()
    if not client:
        return None
    sheet = client.open_by_key(config.SPREADSHEET_ID)
    return sheet.worksheet(sheet_name)

def get_leads_df():
    ws = get_worksheet(config.LEAD_SHEET_NAME)
    if not ws:
        return pd.DataFrame()
    data = ws.get_all_values()
    if not data:
        return pd.DataFrame()
    headers = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=headers)

def update_lead(row_index, field, value):
    ws = get_worksheet(config.LEAD_SHEET_NAME)
    if not ws:
        return
    headers = ws.row_values(1)
    col_idx = headers.index(field) + 1
    ws.update_cell(row_index + 2, col_idx, str(value))

def get_users_df():
    ws = get_worksheet(config.USER_SHEET_NAME)
    if not ws:
        return pd.DataFrame()
    data = ws.get_all_values()
    if not data:
        return pd.DataFrame()
    headers = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=headers)

def get_drive_service():
    creds = get_oauth_creds()
    if not creds:
        return None
    return build("drive", "v3", credentials=creds)

def create_lead_folder(lead_id):
    drive = get_drive_service()
    if not drive:
        return None
    folder_metadata = {"name": f"Lead_{lead_id}", "mimeType": "application/vnd.google-apps.folder"}
    folder = drive.files().create(body=folder_metadata, fields="id").execute()
    return folder.get("id")

def upload_file_to_drive(folder_id, file_bytes, filename):
    drive = get_drive_service()
    if not drive:
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix="_" + filename) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(tmp_path, resumable=True)
    file = drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
    os.unlink(tmp_path)
    return file.get("id")

def get_file_url(file_id):
    return f"https://drive.google.com/file/d/{file_id}/view"

def send_chat_notification(message):
    payload = {"text": message}
    try:
        r = requests.post(config.CHAT_WEBHOOK_URL, json=payload)
        return r.status_code == 200
    except:
        return False
