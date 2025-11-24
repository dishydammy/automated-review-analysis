import os
import gspread
from google.oauth2.service_account import Credentials
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]

def get_google_sheet_client():
    """"Authenticate and return a Google Sheets client."""
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    
    #Add error handling to check if credentials file exists
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Credentials file not found at {creds_path}")
    
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    client = gspread.authorize(creds)
    return client

def get_groq_client():
    """Return an authenticated Groq client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    return Groq(api_key=api_key)
    


if __name__ == "__main__":
    # This block allows you to run 'python src/utils.py' to test connections quickly
        try:
            print("Testing Google Connection...")
            g_client = get_google_sheet_client()
            print("✅ Google Connection Successful!")
            
            print("Testing Groq Connection...")
            groq_client = get_groq_client()
            print("✅ Groq Connection Successful!")
            
        except Exception as e:
            print(f"❌ Connection Failed: {e}")