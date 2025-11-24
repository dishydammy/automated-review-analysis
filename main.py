import sys
import time
from src.etl import load_raw_data, create_staging_data
from src.analysis import process_reviews, generate_analysis

def main():
    """
    Orchestrates the full pipeline:
    1. ETL (Raw -> Staging)
    2. AI Analysis (Staging -> Processed)
    3. Insights (Charts & Stats)
    """
    print("\n" + "="*50)
    print("🚀 STARTING AUTOMATED REVIEW ANALYSIS DEMO")
    print("="*50 + "\n")

    try:
        # --- PHASE 1: ETL ---
        print("📦 PHASE 1: Data Extraction & Transformation")
        # Step 1: Load CSV to Google Sheets (Raw Data)
        spreadsheet = load_raw_data()
        
        # Step 2: Clean and Move to Staging
        create_staging_data(spreadsheet)
        print("✅ Phase 1 Complete.\n")

        # --- PHASE 2: AI ANALYSIS ---
        print("🧠 PHASE 2: AI Sentiment Analysis")
        print("   (This involves sending data to Groq. Please wait...)")
        # Step 3, 5, 6: Run AI pipeline
        processed_df = process_reviews()
        print("✅ Phase 2 Complete.\n")

        # --- PHASE 3: REPORTING ---
        print("📊 PHASE 3: Generating Insights & Charts")
        # Step 7: Generate statistics and save charts
        generate_analysis(processed_df)
        print("✅ Phase 3 Complete.\n")

        print("="*50)
        print("🎉 PIPELINE FINISHED SUCCESSFULLY!")
        print("   1. Check your Google Sheet for the 'processed' tab.")
        print("   2. Check your folder for 'sentiment_distribution_chart.png'.")
        print("="*50)

    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: The pipeline failed.")
        print(f"   Error Detail: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()