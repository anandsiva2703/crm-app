SPREADSHEET_ID = "1YvJTTj6x6UyBN_kZ9sk0IWSfjuGmVQsC6ENoeCWlyDg"
CHAT_WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQAmIvyles/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=0JilMdFxDKQbz-eMBeaa-jxtPKWzILK7QTh46i3A3Cs"
CLIENT_ID = "867129793896-30np6r5hvbase3uqoi1u8no8a4bohgos.apps.googleusercontent.com"
CLIENT_SECRET = "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"

LEAD_SHEET_NAME = "Leads"
USER_SHEET_NAME = "Users"

ROLES = ["Marketing", "Sales", "PMO", "Management"]

VISIBILITY = {
    "Marketing": [
        "Date of lead landed", "Client Name", "Client Contact Number",
        "Site Location", "EB Number", "KW Capacity",
        "Lead Source Platform", "Sales Responsibility", "Current Stage"
    ],
    "Sales": [
        "CRM ID", "Date of lead landed", "Client Name", "Client Contact Number",
        "Site Location", "EB Number", "KW Capacity", "Lead Source Platform",
        "Sales Responsibility", "Current Stage", "Sales Team Remarks",
        "Client Feedback/Remarks", "Latest Quotation Amount",
        "Site Picture", "Site Video", "Site 2D Sketch", "Cable Measurements", "Quotation"
    ],
    "PMO": "ALL",
    "Management": "ALL"
}

FILE_COLUMNS = [
    "Site Picture", "Site Video", "Site 2D Sketch",
    "Quotation", "Preliminary BOM", "BOQ",
    "Work Order", "Commissioning Report", "Warranty Softcopy",
    "Invoice", "Cable Measurements"
]

STAGES = [
    "New lead", "Contacted", "appointment got for site visit",
    "site visit done", "quotation Sent", "Decision pending",
    "Converted", "Order Lost"
]
