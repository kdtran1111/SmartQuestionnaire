from PyPDF2 import PdfReader

# Path to your PDF file
pdf_path = "Screening packet 08312020.pdf"

# Path to save the extracted text
output_txt_path = "extracted_text.txt"

# Load the PDF
reader = PdfReader(pdf_path)

# Extract text from all pages
with open(output_txt_path, "w", encoding="utf-8") as output_file:
    for page_num, page in enumerate(reader.pages, start=1):
        # Write the text of each page into the output file
        output_file.write(f"--- Page {page_num} ---\n")
        output_file.write(page.extract_text() + "\n\n")

print(f"Text extracted and saved to {output_txt_path}")
