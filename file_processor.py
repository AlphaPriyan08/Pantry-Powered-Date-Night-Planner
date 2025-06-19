# file_processor.py

import io
import pypdf
from PIL import Image
from typing import List, Tuple, Dict, Any
from streamlit.runtime.uploaded_file_manager import UploadedFile

def process_uploaded_files(uploaded_files: List[UploadedFile]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Processes a list of uploaded files, separating them into extracted text and image data.

    Args:
        uploaded_files: A list of files from Streamlit's file_uploader.

    Returns:
        A tuple containing:
        - A single string of all extracted text from TXT and PDF files.
        - A list of dictionaries, where each dictionary represents an image
          prepared for a multimodal LLM.
    """
    extracted_text = ""
    image_parts = []

    if not uploaded_files:
        return extracted_text, image_parts

    # Sort files to process text-based ones first, which can provide context
    uploaded_files.sort(key=lambda f: f.name.split('.')[-1].lower() not in ['txt', 'pdf'])

    for file in uploaded_files:
        file_extension = file.name.split('.')[-1].lower()
        file_bytes = file.getvalue()

        if file_extension == "txt":
            extracted_text += f"--- Content from {file.name} ---\n{file_bytes.decode('utf-8')}\n\n"
        
        elif file_extension == "pdf":
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                pdf_text = "".join(page.extract_text() for page in reader.pages)
                extracted_text += f"--- Content from {file.name} ---\n{pdf_text}\n\n"
            except Exception as e:
                extracted_text += f"--- Could not read PDF {file.name}: {e} ---\n\n"

        elif file_extension in ["png", "jpg", "jpeg"]:
            # This is the robust way to prepare image data for Gemini.
            # We provide the raw bytes and the correct MIME type.
            image_parts.append({
                "mime_type": file.type,
                "data": file_bytes
            })

    return extracted_text, image_parts