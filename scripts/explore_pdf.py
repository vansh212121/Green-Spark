# # explore_with_ocr.py
# import fitz  # PyMuPDF
# import pytesseract
# from PIL import Image
# import io

# # --- Configuration for Windows Users ---
# # You might need to tell pytesseract where you installed the Tesseract engine.
# # 1. Download and install Tesseract for Windows from here: https://github.com/UB-Mannheim/tesseract/wiki
# # 2. Find the path to tesseract.exe (e.g., C:/Program Files/Tesseract-OCR/tesseract.exe)
# # 3. Uncomment and update the line below:
# # pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
# # -----------------------------------------


# pdf_path = "bill.pdf"
# output_text_file = "bill_text_ocr_output.txt"

# try:
#     doc = fitz.open(pdf_path)
#     full_text = ""
    
#     print(f"Found {len(doc)} pages in the PDF.")

#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
        
#         # First, try to get normal text
#         text = page.get_text()
#         if text.strip():
#             print(f"Page {page_num + 1} contains standard text.")
#             full_text += text
#             continue

#         # If no text, try to get images and perform OCR
#         print(f"Page {page_num + 1} has no standard text. Attempting OCR on images...")
#         image_list = page.get_images(full=True)
        
#         if not image_list:
#             print(f"No images found on page {page_num + 1}.")
#             continue

#         for img_index, img in enumerate(image_list):
#             xref = img[0]
#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
            
#             # Open the image with Pillow and perform OCR with pytesseract
#             image = Image.open(io.BytesIO(image_bytes))
#             ocr_text = pytesseract.image_to_string(image)
            
#             print(f"Successfully performed OCR on image {img_index + 1} on page {page_num + 1}.")
#             full_text += ocr_text + "\n\n"

#     with open(output_text_file, "w", encoding="utf-8") as f:
#         f.write(full_text)
        
#     print(f"Successfully extracted all text using OCR to '{output_text_file}'")

# except Exception as e:
#     print(f"An error occurred: {e}")








# scripts/explore_pdf.py
import fitz
import pytesseract
from PIL import Image
import io
import os # <-- Add this import

# --- THIS IS THE ROBUST FIX ---
# Get the absolute path of the directory this script is in (e.g., /app/scripts)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Join that directory path with the PDF filename to create a full, unambiguous path
pdf_path = os.path.join(SCRIPT_DIR, "bill.pdf")
# We'll also save the output file in the same directory
output_text_file = os.path.join(SCRIPT_DIR, "bill_text_ocr_output.txt")
# ----------------------------

try:
    doc = fitz.open(pdf_path)
    full_text = ""
    
    print(f"Found {len(doc)} pages in the PDF.")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        print(f"Processing page {page_num + 1}...")
        
        image_list = page.get_images(full=True)
        if not image_list:
            print(f" - No images found on page {page_num + 1}.")
            continue

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            image = Image.open(io.BytesIO(image_bytes))
            ocr_text = pytesseract.image_to_string(image)
            
            print(f" - Successfully performed OCR on image {img_index + 1}.")
            full_text += ocr_text + "\n\n"

    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"\nSuccessfully extracted all text using OCR to '{output_text_file}'")

except Exception as e:
    print(f"An error occurred: {e}")