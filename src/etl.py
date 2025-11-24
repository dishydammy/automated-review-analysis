import pandas as pd
import gspread
from gspread.exceptions import WorksheetNotFound
from src.utils import get_google_sheet_client

CSV_PATH = "Womens Clothing E-Commerce Reviews.csv"
MAIN_SHEET_NAME = "women_clothing_review_sheet"

def load_raw_data():
    """"Loads raw data from csv file and wrtes into the google sheet"""
    print("Starting Step 1: Loading raw data into Google Sheet...")

    #LOAD CSV
    try:
        df = pd.read_csv(CSV_PATH)
        df_subset = df.head(200).copy()

        if "Unnamed: 0" in df_subset.columns:
            df_subset.drop(columns=["Unnamed: 0"], inplace=True)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Could not find {CSV_PATH}.")

    client = get_google_sheet_client()
    
    try:
        spreadsheet = client.open(MAIN_SHEET_NAME)
    except gspread.SpreadsheetNotFound:
        raise ValueError(f"Error: Could not find {MAIN_SHEET_NAME}.")
    
    worksheet_title = "raw_data"

    try:
        worksheet = spreadsheet.worksheet(worksheet_title)
        print(f"Worksheet '{worksheet_title}' found. Clearing existing data...")
        worksheet.clear()
    except WorksheetNotFound:
        print(f"Worksheet '{worksheet_title}' not found. Creating a new one...")
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="250", cols="20")
    
    # Fill NaN with empty strings
    df_subset = df_subset.fillna("")
    data_to_upload = [df_subset.columns.values.tolist()] + df_subset.values.tolist()
    worksheet.update(range_name="A1", values=data_to_upload)
    
    print("✅ Step 1 Complete: Raw data loaded and protected.")
    return spreadsheet


def create_staging_data(spreadsheet):
    """Pulls data from raw_data worksheet, does basic cleaning, and writes to staging_data worksheet"""
    print("Starting Step 2: Creating staging data...")

    raw_worksheet = spreadsheet.worksheet("raw_data")
    data = raw_worksheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("Error: Raw data worksheet is empty.")
    
    df_cleaned = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        
    # HAndle staging Worksheet
    worksheet_title = "staging"

    try:
        worksheet = spreadsheet.worksheet(worksheet_title)
        print(f"Worksheet '{worksheet_title}' found. Clearing existing data...")
        worksheet.clear()
    except WorksheetNotFound:
        print(f"Worksheet '{worksheet_title}' not found. Creating a new one...")
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="250", cols="20")
        
    #Upload Staging Data
    df_cleaned = df_cleaned.astype(str)
    data_to_upload = [df_cleaned.columns.values.tolist()] + df_cleaned.values.tolist()
    worksheet.update(range_name="A1", values=data_to_upload)
    print("✅ Step 2 Complete: Staging data created.")
    
if __name__ == "__main__":
    try:
        sh = load_raw_data()
        create_staging_data(sh)
    except Exception as e:
        print(f"\n X Pipeline failed: {e}")
    
    


        





