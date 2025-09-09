import csv
import os
import shutil
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURATION ---
SERVICE_ACCOUNT_FILE = os.path.join(os.environ.get("HOME"), ".credentials", "service_account.json")
SPREADSHEET_ID = "1uBOtnYkDAMuLwwGkWgTnrroryuW97SAR7bDlxL-GFAw"

CSV_SOURCE_DIR = "csv_to_process"
SOURCE_VERSIONS_DIR = "source_versions"
PROCESSED_DIR = "processed"

LOG_SHEET_NAME = "logs"

# --- AUTHENTIFICATION ---
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# --- Créer onglet logs si inexistant ---
try:
    log_ws = spreadsheet.worksheet(LOG_SHEET_NAME)
except gspread.WorksheetNotFound:
    log_ws = spreadsheet.add_worksheet(title=LOG_SHEET_NAME, rows="1000", cols="10")
    log_ws.append_row(["CSV Source", "Timestamp", "Onglet", "Lignes ajoutées", "Version"])

# --- Fonction utilitaire pour versionner ---
def get_versioned_filename(folder, base_name, suffix=""):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    version = 1
    while True:
        filename = f"{base_name}_{now}_v{version}{suffix}.csv"
        if not os.path.exists(os.path.join(folder, filename)):
            return filename
        version += 1

# --- Traiter chaque CSV dans csv_to_process/ ---
for csv_file in os.listdir(CSV_SOURCE_DIR):
    if not csv_file.endswith(".csv"):
        continue

    base_name = os.path.splitext(csv_file)[0]

    # --- Versionner le CSV source ---
    os.makedirs(SOURCE_VERSIONS_DIR, exist_ok=True)
    source_versioned = get_versioned_filename(SOURCE_VERSIONS_DIR, base_name)
    shutil.move(os.path.join(CSV_SOURCE_DIR, csv_file), os.path.join(SOURCE_VERSIONS_DIR, source_versioned))
    print(f"✅ CSV source versionné : {source_versioned}")

    # --- Versionner le CSV processed ---
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    processed_versioned = get_versioned_filename(PROCESSED_DIR, base_name, suffix="_transcribed")
    shutil.copyfile(os.path.join(SOURCE_VERSIONS_DIR, source_versioned),
                    os.path.join(PROCESSED_DIR, processed_versioned))
    print(f"✅ CSV processed créé : {processed_versioned}")

    # --- Ajouter dans Google Sheets ---
    try:
        ws = spreadsheet.worksheet(base_name)
        print(f"📌 Onglet '{base_name}' trouvé, ajout des lignes…")
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=base_name, rows="1000", cols="20")
        print(f"📌 Onglet '{base_name}' créé.")

    # Lire le CSV processed
    with open(os.path.join(PROCESSED_DIR, processed_versioned), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)

    # Ajouter les lignes
    ws.append_rows(data, value_input_option="USER_ENTERED")
    lines_added = len(data)

    # --- Log ---
    log_ws.append_row([
        processed_versioned,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        base_name,
        lines_added,
        processed_versioned.split("_v")[-1].split(".")[0]
    ])
    print(f"📝 Log mis à jour pour '{processed_versioned}'")
