import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.analysis import analyze_review, process_reviews, generate_analysis


def test_analyze_review_success():
    """Test that analyze_review correctly calls Groq and returns content."""
    mock_client = MagicMock()
    
    # Mock the nested response structure
    mock_response_obj = MagicMock()
    mock_response_obj.choices[0].message.content = "Positive | Great summary"
    mock_client.chat.completions.create.return_value = mock_response_obj
    
    result = analyze_review("Test text", mock_client)
    
    assert result == "Positive | Great summary"

def test_analyze_review_api_failure():
    """Test that the function returns a safe fallback if Groq API fails."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Down")
    
    result = analyze_review("Test text", mock_client)
    
    assert "Analysis failed" in result


@patch("src.analysis.get_google_sheet_client")
@patch("src.analysis.get_groq_client")
@patch("src.analysis.analyze_review")
@patch("src.analysis.time.sleep")
def test_process_reviews(mock_sleep, mock_analyze, mock_get_groq, mock_get_sheet):
    """Test the full loop: Reading Staging -> Processing -> Writing Processed."""
    
    mock_sheet_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_staging_sheet = MagicMock()
    mock_processed_sheet = MagicMock()
    
    mock_get_sheet.return_value = mock_sheet_client
    mock_sheet_client.open.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.side_effect = [mock_staging_sheet, mock_processed_sheet]
    
    mock_staging_sheet.get_all_records.return_value = [
        {"Review Text": "I love it"}, 
        {"Review Text": "I hate it"},
        {"Review Text": ""} 
    ]
    
    mock_analyze.side_effect = ["Positive | Loved it", "Negative | Hated it"]
    
    df_result = process_reviews()
    
    assert df_result.iloc[0]["AI Sentiment"] == "Positive"
    assert df_result.iloc[0]["Action Needed"] == "No"
    
    assert df_result.iloc[1]["AI Sentiment"] == "Negative"
    assert df_result.iloc[1]["Action Needed"] == "Yes"
    
    assert df_result.iloc[2]["AI Sentiment"] == "Neutral"
    assert df_result.iloc[2]["AI Summary"] == "No Review Text available." 
    
    mock_processed_sheet.update.assert_called()


@patch("src.analysis.plt")
def test_generate_analysis(mock_plt):
    """Test that insights are generated and charts saved."""
    df = pd.DataFrame({
        "Class Name": ["Dresses", "Dresses", "Blouses"],
        "AI Sentiment": ["Positive", "Negative", "Positive"]
    })
    
    generate_analysis(df)
    mock_plt.savefig.assert_called_with("sentiment_distribution_chart.png")

def test_generate_analysis_missing_column(capsys):
    """Test graceful exit if Class Name is missing."""
    df = pd.DataFrame({"Wrong Column": [1, 2, 3]})
    generate_analysis(df)
    
    captured = capsys.readouterr()
    assert "Class Name column missing" in captured.out