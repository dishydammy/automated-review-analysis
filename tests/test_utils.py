import pytest
from unittest.mock import patch, MagicMock
from src.utils import get_google_sheet_client, get_groq_client

# --- Test 1: Google Client Success ---
@patch("src.utils.gspread")
@patch("src.utils.Credentials")   
@patch("src.utils.os.path.exists") 
@patch("src.utils.os.getenv")      
def test_get_google_sheet_client_success(mock_getenv, mock_exists, mock_creds, mock_gspread):
    mock_getenv.return_value = "dummy_creds.json"
    mock_exists.return_value = True 
    
    client = get_google_sheet_client()
    
    mock_getenv.assert_any_call("GOOGLE_CREDENTIALS_PATH")
    mock_creds.from_service_account_file.assert_called_once()
    mock_gspread.authorize.assert_called_once()
    assert client is not None

@patch("src.utils.os.path.exists")
@patch("src.utils.os.getenv")
def test_get_google_sheet_client_file_not_found(mock_getenv, mock_exists):
    mock_getenv.return_value = "missing_file.json"
    mock_exists.return_value = False # Pretend file is missing
    
    with pytest.raises(FileNotFoundError):
        get_google_sheet_client()

@patch("src.utils.Groq")
@patch("src.utils.os.getenv")
def test_get_groq_client_success(mock_getenv, mock_groq):
    mock_getenv.return_value = "gsk_fake_key"
    client = get_groq_client()
    
    mock_getenv.assert_called_with("GROQ_API_KEY")
    mock_groq.assert_called_once_with(api_key="gsk_fake_key")
    assert client is not None

@patch("src.utils.os.getenv")
def test_get_groq_client_no_key(mock_getenv):
    mock_getenv.return_value = None

    with pytest.raises(ValueError):
        get_groq_client()