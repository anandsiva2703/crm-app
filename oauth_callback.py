import requests
import config
from urllib.parse import urlencode

def get_auth_url():
    params = {
        "client_id": config.CLIENT_ID,
        "redirect_uri": "https://crm-app-500313.streamlit.app/oauth2callback",
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.email",
        "access_type": "offline",
        "prompt": "consent"
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

def exchange_code_for_token(code):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET,
        "redirect_uri": "https://crm-app-500313.streamlit.app/oauth2callback",
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    return response.json()
