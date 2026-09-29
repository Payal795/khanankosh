from hybrid_ocr import MultiTierHybridOCR

if __name__ == "__main__":
    pipeline = MultiTierHybridOCR()
    pdf_file = "sample_scanned_report.pdf"  # Replace with your test PDF
    
    print("Starting Multi-Tier OCR Processing...")
    output = pipeline.process_pdf(pdf_file)
    
    for res in output:
        print(f"\n--- Page {res['page']} [{res['tier']}] ---")
        print(res['text'][:300])  # Print first 300 characters