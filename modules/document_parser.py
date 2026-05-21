"""
Document Parser Module
Handles parsing and extraction of information from various document formats.
"""

import pdfplumber
import pytesseract
from PIL import Image
import io
import os
from typing import Union
try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None


class DocumentParser:
    """Parse and extract data from loan-related documents."""

    def __init__(self):
        """Initialize the document parser."""
        self.supported_formats = ['.pdf', '.txt', '.png', '.jpg', '.jpeg', '.doc', '.docx']
        self._configure_tesseract()
    
    def _configure_tesseract(self):
        """Configure Tesseract path if it exists on common Windows locations."""
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.pytesseract_cmd = path
                break

    def parse_document(self, file_content: Union[bytes, str], file_name: str) -> dict:
        """
        Parse a document and extract relevant information.
        
        Args:
            file_content: File content as bytes or file path as string
            file_name (str): Name of the document file
            
        Returns:
            dict: Extracted document data
        """
        file_extension = '.' + file_name.split('.')[-1].lower()
        
        if not self.validate_format(file_name):
            return {"error": f"Unsupported file format: {file_extension}"}
        
        try:
            if file_extension == '.pdf':
                return {"text": self.extract_pdf(file_content)}
            elif file_extension in ['.png', '.jpg', '.jpeg']:
                return {"text": self.extract_image(file_content)}
            elif file_extension == '.txt':
                return {"text": file_content.decode('utf-8') if isinstance(file_content, bytes) else file_content}
            elif file_extension in ['.doc', '.docx']:
                return {"text": self.extract_docx(file_content)}
        except Exception as e:
            return {"error": f"Failed to parse document: {str(e)}"}
        
        return {"error": "Unknown error"}

    def extract_text(self, file_content: bytes, file_name: str) -> str:
        """
        Extract text content from a document.
        
        Args:
            file_content (bytes): File content as bytes
            file_name (str): Name of the document file
            
        Returns:
            str: Extracted text content
        """
        result = self.parse_document(file_content, file_name)
        return result.get("text", "")

    def extract_pdf(self, file_content: bytes) -> str:
        """
        Extract text from PDF using pdfplumber.
        
        Args:
            file_content (bytes): PDF file content
            
        Returns:
            str: Extracted text
        """
        text = ""
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n"
        except Exception as e:
            raise Exception(f"PDF parsing error: {str(e)}")
        
        return text.strip()

    def extract_image(self, file_content: bytes) -> str:
        """
        Extract text from image using pytesseract OCR.
        
        Args:
            file_content (bytes): Image file content
            
        Returns:
            str: Extracted text
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            error_msg = str(e)
            if "tesseract" in error_msg.lower():
                raise Exception(
                    "Tesseract OCR is not installed. Please install it:\n"
                    "Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki and install to "
                    "C:\\Program Files\\Tesseract-OCR\n"
                    "Or use: choco install tesseract (if you have Chocolatey)\n"
                    "Linux: sudo apt-get install tesseract-ocr\n"
                    "macOS: brew install tesseract"
                )
            raise Exception(f"Image parsing error: {error_msg}")

    def extract_docx(self, file_content: bytes) -> str:
        """
        Extract text from Word document (.doc, .docx).
        
        Args:
            file_content (bytes): Word document file content
            
        Returns:
            str: Extracted text
        """
        try:
            if DocxDocument is None:
                raise Exception("python-docx is not installed. Install it using: pip install python-docx")
            
            # Create a BytesIO object from the file content
            doc_file = io.BytesIO(file_content)
            
            # Open the document
            doc = DocxDocument(doc_file)
            
            # Extract all text from paragraphs
            text = "\n".join([para.text for para in doc.paragraphs])
            
            # Also extract text from tables if present
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += "\n" + cell.text
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Word document parsing error: {str(e)}")

    def validate_format(self, file_name: str) -> bool:
        """
        Validate if the document format is supported.
        
        Args:
            file_name (str): Name of the document file
            
        Returns:
            bool: True if format is supported, False otherwise
        """
        file_extension = '.' + file_name.split('.')[-1].lower()
        return file_extension in self.supported_formats
