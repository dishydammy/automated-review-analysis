import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.etl import load_raw_data, create_staging_data
from gspread.exceptions import WorksheetNotFound

MOCK_CSV_DATA = pd.DataFrame({
    "Unnamed: 0": [0, 1],
    "Clothing ID": [101, 102],
    "Review Text": ["Great", "Okay"]
})

@patch("src.etl.get_google_sheet_client")
@patch("src.etl.pd.read_csv")
def test_load_raw_data_success(mock_read_csv, mock_get_client):
    """Test that CSV is read and uploaded to raw_data sheet."""
    mock_read_csv.return_value = MOCK_CSV_DATA
    
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    
    mock_get_client.return_value = mock_client
    mock_client.open.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.return_value = mock_worksheet
    
    returned_spreadsheet = load_raw_data()
    
    mock_read_csv.assert_called_once()
    mock_client.open.assert_called_with("women_clothing_review_sheet")
    mock_worksheet.clear.assert_called_once()
    mock_worksheet.update.assert_called()
    assert returned_spreadsheet == mock_spreadsheet

@patch("src.etl.pd.read_csv")
def test_load_raw_data_file_not_found(mock_read_csv):
    """Test error handling when CSV is missing."""
    mock_read_csv.side_effect = FileNotFoundError
    
    with pytest.raises(FileNotFoundError):
        load_raw_data()


def test_create_staging_data_success():
    """Test reading raw_data, cleaning it, and writing to staging."""
    mock_spreadsheet = MagicMock()
    mock_raw_sheet = MagicMock()
    mock_staging_sheet = MagicMock()
    
    mock_spreadsheet.worksheet.side_effect = [mock_raw_sheet, mock_staging_sheet]
    
    mock_raw_sheet.get_all_records.return_value = [
        {"Clothing ID": " 123 ", "Review Text": "  Messy Text  "}
    ]
    
    create_staging_data(mock_spreadsheet)
    
    mock_spreadsheet.worksheet.assert_any_call("raw_data")
    
    _, kwargs = mock_staging_sheet.update.call_args
    uploaded_values = kwargs['values']
    
    row_data = uploaded_values[1]
    
    assert "Messy Text" in row_data 
    assert "123" in row_data