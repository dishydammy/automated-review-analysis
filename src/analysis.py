import pandas as pd
import time
import matplotlib.pyplot as plt
from src.utils import get_google_sheet_client, get_groq_client

SHEET_NAME = 'women_clothing_review_sheet'
GROQ_MODEL = "llama-3.1-8b-instant"

def analyze_review(text, client):
    """Sends review text to Groq LLM for sentiment analysis."""
    
    prompt = f"""
    You are a data extraction bot. You do not explain. You do not chat.
    
    Task: Analyze the sentiment of the text below.
    Format: Return ONLY the Sentiment (Positive/Negative/Neutral) followed by a pipe (|) and a 1-sentence summary.
    
    Example Output: Positive | The customer loved the fabric and fit.
    
    Review Text: "{text}"
    
    Your Output:
    """

    try:
        completion = client.chat.completions.create(
            messages = [{'role': 'user', 'content': prompt}],
            model = GROQ_MODEL,
            temperature = 0.1
        )
        response = completion.choices[0].message.content.strip()
        
        #Print first 60 chars of response for debugging
        print(f" Raw Response: {response[:60]}...")
        return response
    except Exception as e:
        print(f"Error during Groq API call: {e}")
        return "Neutral | Analysis failed."
    
    
def process_reviews():
    """Reads staging data, runs AI Analysis, calculates 'Action needed' and writes to processed sheet."""
    print("Starting Step 3: AI Analysis of Reviews")

    sheet_client = get_google_sheet_client()
    groq_client = get_groq_client()
    spreadsheet = sheet_client.open(SHEET_NAME)

    staging_worksheet = spreadsheet.worksheet('staging')
    data = staging_worksheet.get_all_records()
    df = pd.DataFrame(data)

    print(f"Processing {len(df)} reviews...")

    # Iterate and Analyze
    sentiments = []
    summaries = []
    actions = []

    for index, row in df.iterrows():
        text = str(row.get("Review Text", "")).strip()

        if not text or text.lower() == "nan":
            sentiments.append("Neutral")
            summaries.append("No Review Text available.")
            actions.append("No")
            continue

        response = analyze_review(text, groq_client)

        if "|" in response:
            parts = response.split("|", 1)
            sentiment = parts[0].strip().replace(".", "").title()
            summary = parts[1].strip()
        else:
            sentiment = "Neutral"
            summary = response
        
        if sentiment == 'Negative':
            action = "Yes"
        else:
            action = "No"

        sentiments.append(sentiment)
        summaries.append(summary)
        actions.append(action)

        #Rate Limiting Handling
        time.sleep(0.4)
        if index % 10 == 0:
            print(f"        Analyzed row {index}. .....")

    # Add results to DataFrame
    df["AI Sentiment"] = sentiments
    df["AI Summary"] = summaries
    df["Action Needed"] = actions

    # Write to processed worksheet
    try:
        proc_sheet = spreadsheet.worksheet('processed')
        print( "Clearing processed sheet....")
        proc_sheet.clear()
    except:
        print("Processed sheet not found. Creating new one...")
        proc_sheet = spreadsheet.add_worksheet(title='processed', rows=len(df)+50, cols=20)
    
    df = df.astype(str)
    data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
    proc_sheet.update(range_name='A1', values=data_to_upload)

    print("Analysis Complete. Results written to 'processed' sheet.")
    return df


def generate_analysis(df):
    """Analytical Insights & Charts."""
    print("\n Generating Analytical Insights...")

    # Ensure classification columns are present
    if "Class Name" not in df.columns:
        print("Class Name column missing. Skipping analysis.")
        return
    
    # Percentage Distribution of Sentiments by Class
    print("\n --- Sentiment Breakdown by Class ---")
    breakdown = pd.crosstab(df['Class Name'], df['AI Sentiment'], normalize='index') * 100
    print(breakdown.round(2))

    # Highest Sentiments
    print("\n--- Top Performers ---")
    counts = pd.crosstab(df['Class Name'], df["AI Sentiment"])

    if 'Positive' in counts.columns:
        top_positive = counts['Positive'].idxmax()
        print(f"Class with Highest Positive Reviews: {top_positive}")
    
    if 'Negative' in counts.columns:
        top_negative = counts['Negative'].idxmax()
        print(f"Class with Highest Negative Reviews: {top_negative}")

    
    # Generate Chart
    top_classes = df['Class Name'].value_counts().head(5).index
    subset = df[df['Class Name'].isin(top_classes)]

    plt.figure(figsize=(10,6))
    pd.crosstab(subset['Class Name'], subset['AI Sentiment']).plot(kind='bar', stacked=True)
    plt.title("Sentiment Distribution for Top 5 Classes")
    plt.ylabel("Number of Reviews")
    plt.xlabel("Class Name")
    plt.tight_layout()

    plt.savefig("sentiment_distribution_chart.png")
    print("\n Chart saved as 'sentiment_distribution_chart.png'")

if __name__ == "__main__":
    processed_df = process_reviews()
    generate_analysis(processed_df)
