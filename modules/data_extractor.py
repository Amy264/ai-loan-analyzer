"""
Data Extractor Module
Extracts structured data from loan documents using category-specific prompts.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import json
from dotenv import load_dotenv
from .prompt_loader import load_prompt

load_dotenv()


class DataExtractor:
    """Extract structured data from loan documents using AI."""
    
    def __init__(self, model: str = "openrouter/auto"):
        """
        Initialize the DataExtractor with OpenRouter API.
        
        Args:
            model (str): The OpenRouter model to use. Defaults to "openrouter/auto".
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Category-specific extraction prompts loaded from external files
        self.extraction_prompts = {
            "Salary & Employment Contract": PromptTemplate(
                input_variables=["document_text"],
                template=load_prompt("prompts/data_extraction/salary_employment.txt")
            ),
            
            "Personal Information": PromptTemplate(
                input_variables=["document_text"],
                template=load_prompt("prompts/data_extraction/personal_information.txt")
            ),
            
            "Asset Valuation Information": PromptTemplate(
                input_variables=["document_text"],
                template=load_prompt("prompts/data_extraction/asset_valuation.txt")
            ),
            
            "CIC/Credit Report": PromptTemplate(
                input_variables=["document_text"],
                template=load_prompt("prompts/data_extraction/credit_report.txt")
            )
        }
    
    def extract_data(self, document_text: str, category: str) -> dict:
        """
        Extract structured data from a document based on its category.
        
        Args:
            document_text (str): The document text to extract data from
            category (str): The document category (must be a key in extraction_prompts)
            
        Returns:
            dict: Extracted data in JSON format
        """
        if category not in self.extraction_prompts:
            return {
                "error": f"Unknown category: {category}. "
                         f"Available categories: {', '.join(self.extraction_prompts.keys())}"
            }
        
        try:
            prompt = self.extraction_prompts[category]
            formatted_prompt = prompt.format(document_text=document_text)
            
            response = self.llm.invoke(formatted_prompt)
            response_text = response.content.strip()
            
            # Clean up response text - remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Try to parse the response as JSON
            try:
                # Find JSON object in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    extracted_data = json.loads(json_str)
                    
                    # Validate that extracted data is a dict
                    if not isinstance(extracted_data, dict):
                        return {
                            "category": category,
                            "success": False,
                            "error": "Response is not a JSON object",
                            "raw_response": response_text
                        }
                    
                    return {
                        "category": category,
                        "success": True,
                        "data": extracted_data
                    }
                else:
                    return {
                        "category": category,
                        "success": False,
                        "error": "No JSON object found in response. Please check if AI returned valid JSON.",
                        "raw_response": response_text[:500] if len(response_text) > 500 else response_text
                    }
            except json.JSONDecodeError as e:
                return {
                    "category": category,
                    "success": False,
                    "error": f"JSON parsing error on line {e.lineno}: {e.msg}",
                    "raw_response": response_text[:500] if len(response_text) > 500 else response_text
                }
        
        except Exception as e:
            return {
                "category": category,
                "success": False,
                "error": f"Extraction error: {str(e)}"
            }
    
    def extract_from_multiple_documents(self, documents: list) -> list:
        """
        Extract data from multiple documents.
        
        Args:
            documents (list): List of tuples (document_text, category)
            
        Returns:
            list: List of extracted data dictionaries
        """
        results = []
        for document_text, category in documents:
            result = self.extract_data(document_text, category)
            results.append(result)
        
        return results
