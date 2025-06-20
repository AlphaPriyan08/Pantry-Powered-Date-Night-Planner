import io
import pypdf
import base64 
from typing import List, Tuple, Dict, Any, Optional
from streamlit.runtime.uploaded_file_manager import UploadedFile

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024 

def process_uploaded_files(
    uploaded_files: List[UploadedFile], 
    st_object: Optional[Any] = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Processes a list of uploaded files, separating them into extracted text and 
    Base64-encoded image data conforming to the LangChain schema.

    Args:
        uploaded_files: A list of files from Streamlit's file_uploader.
        st_object: The Streamlit module object, passed in to display warnings.

    Returns:
        A tuple containing:
        - A single string of all extracted text from TXT and PDF files.
        - A list of dictionaries, where each dictionary represents an image
          prepared for a multimodal LLM in the correct format.
    """
    extracted_text = ""
    image_parts = []

    if not uploaded_files:
        return extracted_text, image_parts

    for file in uploaded_files:
        if file.size > MAX_FILE_SIZE_BYTES:
            if st_object:
                st_object.warning(f"Skipped {file.name}: File is larger than the {MAX_FILE_SIZE_BYTES/1024/1024:.0f}MB limit.")
            continue

        file_extension = file.name.split('.')[-1].lower()
        file_bytes = file.getvalue()

        if file_extension == "txt":
            try:
                extracted_text += f"--- Content from {file.name} ---\n{file_bytes.decode('utf-8')}\n\n"
            except UnicodeDecodeError:
                if st_object:
                    st_object.warning(f"Could not decode {file.name} as text. It might be a binary file.")
        
        elif file_extension == "pdf":
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                pdf_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
                if pdf_text:
                    extracted_text += f"--- Content from {file.name} ---\n{pdf_text}\n\n"
                else:
                    if st_object:
                        st_object.warning(f"Could not extract any text from {file.name}. It may be an image-based PDF.")
            except Exception as e:
                if st_object:
                    st_object.error(f"Failed to read PDF {file.name}: {e}")

        elif file_extension in ["png", "jpg", "jpeg"]:

            # 1. Encode the image bytes to a Base64 string.
            base64_image = base64.b64encode(file_bytes).decode("utf-8")
            
            # 2. Create the dictionary in the correct format that LangChain expects.
            image_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{file.type};base64,{base64_image}"
                }
            })

    return extracted_text, image_parts