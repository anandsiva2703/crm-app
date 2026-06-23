import streamlit as st
import pandas as pd
import plotly.express as px
from google_utils import *
import config
import requests
import urllib.parse

st.set_page_config(page_title="CRM Dashboard", layout="wide")

# ---------- OAuth Login ----------
def login_with_google():
    st.title("🔐 CRM Login")
    st.write("Click the button below to log in with your Google account.")
    params = {
        "client_id": config.CLIENT_ID,
        "redirect_uri": "https://crm-app-500313.streamlit.app/oauth2callback",
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.email",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    st.markdown(f'<a href="{auth_url}" target="_self"><button style="background-color:#4285F4; color:white; padding:10px 24px; border:none; border-radius:4px; font-size:16px; cursor:pointer;">🔑 Login with Google</button></a>', unsafe_allow_html=True)
    return False

if "oauth_creds" not in st.session_state:
    st.session_state.oauth_creds = None

if st.session_state.oauth_creds is None:
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
            "redirect_uri": "https://crm-app-500313.streamlit.app/oauth2callback",
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=data)
        token_data = response.json()
        if "access_token" in token_data:
            st.session_state.oauth_creds = {
                "token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "client_id": config.CLIENT_ID,
                "client_secret": config.CLIENT_SECRET
            }
            st.query_params.clear()
            st.rerun()
        else:
            st.error("Login failed. Please try again.")
            st.stop()
    else:
        login_with_google()
        st.stop()

# ---------- App Setup ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None
if "leads_df" not in st.session_state:
    st.session_state.leads_df = get_leads_df()
if "users_df" not in st.session_state:
    st.session_state.users_df = get_users_df()
if "selected_crm" not in st.session_state:
    st.session_state.selected_crm = None

def email_login():
    st.sidebar.title("👤 User Selection")
    email = st.sidebar.text_input("Enter your email (as in Users sheet)")
    if st.sidebar.button("Access CRM"):
        users = st.session_state.users_df
        if "Email" not in users.columns:
            st.sidebar.error("Users sheet missing 'Email' column")
            return
        user_row = users[users["Email"] == email]
        if not user_row.empty:
            st.session_state.user = email
            st.session_state.role = user_row.iloc[0]["team"]
            st.rerun()
        else:
            st.sidebar.error("Email not found in Users sheet.")

if st.session_state.user is None:
    email_login()
    st.stop()

# ---------- Main App ----------
st.title(f"📊 CRM Dashboard – {st.session_state.role}")

if st.button("🔄 Refresh Data"):
    st.session_state.leads_df = get_leads_df()
    st.rerun()

df = st.session_state.leads_df.copy()
role = st.session_state.role

if role == "Sales":
    user_name = st.session_state.users_df[st.session_state.users_df["Email"] == st.session_state.user].iloc[0]["Name"]
    if "Sales Responsibility" in df.columns:
        df = df[df["Sales Responsibility"] == user_name]

visible_cols = config.VISIBILITY.get(role, [])
if visible_cols == "ALL":
    visible_cols = df.columns.tolist()
if "CRM ID" in visible_cols:
    visible_cols = ["CRM ID"] + [c for c in visible_cols if c != "CRM ID"]
if role == "Marketing":
    visible_cols = [c for c in visible_cols if c not in config.FILE_COLUMNS]
visible_cols = [c for c in visible_cols if c in df.columns]
display_df = df[visible_cols].copy()

st.subheader("🔎 Filter Leads")
col1, col2 = st.columns(2)
with col1:
    stage_filter = st.selectbox("Stage", options=["All"] + config.STAGES)
with col2:
    if "Date of lead landed" in df.columns:
        date_range = st.date_input("Date range", value=[])
    else:
        date_range = []

if stage_filter != "All":
    display_df = display_df[display_df["Current Stage"] == stage_filter]
if len(date_range) == 2:
    start, end = date_range
    display_df["Date of lead landed"] = pd.to_datetime(display_df["Date of lead landed"])
    display_df = display_df[(display_df["Date of lead landed"] >= pd.to_datetime(start)) &
                            (display_df["Date of lead landed"] <= pd.to_datetime(end))]

st.subheader("📋 Leads")
for idx, row in display_df.iterrows():
    crm_id = row["CRM ID"]
    if st.button(f"🔍 {crm_id}", key=f"btn_{crm_id}"):
        st.session_state.selected_crm = crm_id
        st.rerun()

st.dataframe(display_df, use_container_width=True)

if st.session_state.selected_crm:
    crm_id = st.session_state.selected_crm
    st.subheader(f"📄 Lead Details – {crm_id}")
    lead_row = df[df["CRM ID"] == crm_id]
    if lead_row.empty:
        st.error("Lead not found")
        st.session_state.selected_crm = None
        st.rerun()
    lead_row = lead_row.iloc[0]

    if role == "Marketing":
        show_fields = config.VISIBILITY["Marketing"]
    elif role == "Sales":
        show_fields = [c for c in df.columns if c not in ["PMO Team Remarks"]]
    else:
        show_fields = df.columns.tolist()
    if role == "Marketing":
        show_fields = [c for c in show_fields if c not in config.FILE_COLUMNS]
    show_fields = [c for c in show_fields if c in df.columns]

    with st.form(key="detail_form"):
        edited = {}
        row_idx = df.index[df["CRM ID"] == crm_id][0]

        for field in show_fields:
            current_val = lead_row[field] if field in lead_row.index else ""
            if field in config.FILE_COLUMNS:
                if pd.notna(current_val) and str(current_val).strip() != "":
                    st.write(f"📎 [{field}]({get_file_url(current_val)})")
                else:
                    st.write(f"📎 {field}: No file uploaded")
                upload_allowed = False
                if role == "Sales" and field in ["Site Picture", "Site Video", "Site 2D Sketch", "Cable Measurements", "Quotation"]:
                    upload_allowed = True
                elif role in ["PMO", "Management"] and field in config.FILE_COLUMNS:
                    upload_allowed = True
                if upload_allowed:
                    uploaded = st.file_uploader(f"Upload {field}", key=f"upload_{field}_{crm_id}")
                    if uploaded:
                        folder_id = lead_row.get("Drive Folder ID", "")
                        if pd.isna(folder_id) or folder_id == "":
                            folder_id = create_lead_folder(crm_id)
                            update_lead(row_idx, "Drive Folder ID", folder_id)
                        file_id = upload_file_to_drive(folder_id, uploaded.read(), uploaded.name)
                        edited[field] = file_id
                        st.success(f"Uploaded {field} successfully!")

            elif field == "Current Stage":
                new_stage = st.selectbox(field, config.STAGES, index=config.STAGES.index(current_val) if current_val in config.STAGES else 0)
                if new_stage != current_val:
                    edited[field] = new_stage
                    user_name = st.session_state.users_df[st.session_state.users_df["Email"] == st.session_state.user].iloc[0]["Name"]
                    msg = f"📢 Lead {crm_id} stage changed from '{current_val}' to '{new_stage}' by {user_name}"
                    send_chat_notification(msg)
            else:
                if field == "Date of lead landed":
                    val = st.date_input(field, value=pd.to_datetime(current_val) if pd.notna(current_val) and current_val != "" else None)
                    edited[field] = val.strftime("%Y-%m-%d") if val else ""
                elif field == "Latest Quotation Amount":
                    try:
                        default_val = float(current_val) if current_val not in ["", None] else 0.0
                    except:
                        default_val = 0.0
                    val = st.number_input(field, value=default_val)
                    edited[field] = val
                else:
                    val = st.text_input(field, value=str(current_val) if pd.notna(current_val) else "")
                    edited[field] = val

        if st.form_submit_button("💾 Save Changes"):
            for field, value in edited.items():
                if field != "Current Stage":
                    update_lead(row_idx, field, value)
            if "Current Stage" in edited:
                update_lead(row_idx, "Current Stage", edited["Current Stage"])
            st.success("✅ Lead updated successfully!")
            st.session_state.leads_df = get_leads_df()
            st.rerun()

    if st.button("❌ Close Details"):
        st.session_state.selected_crm = None
        st.rerun()

st.subheader("📈 Lead Funnel & Distribution")
if "Current Stage" in df.columns:
    stage_counts = df["Current Stage"].value_counts().reset_index()
    stage_counts.columns = ["Stage", "Count"]
    all_stages = pd.DataFrame({"Stage": config.STAGES})
    stage_counts = all_stages.merge(stage_counts, on="Stage", how="left").fillna(0)
    fig1 = px.funnel(stage_counts, x="Count", y="Stage", title="Conversion Funnel")
    st.plotly_chart(fig1)
    fig2 = px.pie(stage_counts, values="Count", names="Stage", title="Stage Distribution")
    st.plotly_chart(fig2)
else:
    st.info("No stage data to display.")
