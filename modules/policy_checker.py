"""
Policy Checker Module
Validates extracted loan data against loan policy guidelines.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import json
from dotenv import load_dotenv
from .prompt_loader import load_prompt

load_dotenv()


class PolicyChecker:
    """Check loan policy compliance using AI."""
    
    def __init__(self, policy_file: str = "data/loan_policy.txt"):
        """
        Initialize the PolicyChecker with loan policy.
        
        Args:
            policy_file (str): Path to the loan policy file
        """
        self.policy_content = self._load_policy(policy_file)
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(
            model="openrouter/auto",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Load prompt from external file
        prompt_template = load_prompt("prompts/policy_check.txt")
        self.policy_check_prompt = PromptTemplate(
            input_variables=["policy", "document_text", "document_category"],
            template=prompt_template
        )
    
    def _load_policy(self, policy_file: str) -> str:
        """
        Load loan policy from file.
        
        Args:
            policy_file (str): Path to the policy file
            
        Returns:
            str: Policy content
        """
        try:
            with open(policy_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "No policy file found. Using default policy checking."
        except Exception as e:
            raise Exception(f"Error loading policy file: {str(e)}")
    
    def check_compliance(self, document_text: str, document_category: str) -> dict:
        """
        Check if document complies with loan policies.
        
        Args:
            document_text (str): Extracted document text
            document_category (str): Category of the document
            
        Returns:
            dict: Compliance check results
        """
        try:
            formatted_prompt = self.policy_check_prompt.format(
                policy=self.policy_content,
                document_text=document_text,
                document_category=document_category
            )
            
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
                    result = json.loads(json_str)
                    
                    # Validate that result is a dict
                    if not isinstance(result, dict):
                        return {
                            "success": False,
                            "category": document_category,
                            "error": "Response is not a JSON object",
                            "raw_response": response_text[:500] if len(response_text) > 500 else response_text
                        }
                    
                    return {
                        "success": True,
                        "category": document_category,
                        "data": result
                    }
                else:
                    return {
                        "success": False,
                        "category": document_category,
                        "error": "No JSON object found in response. Please ensure policy data is properly formatted.",
                        "raw_response": response_text[:500] if len(response_text) > 500 else response_text
                    }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "category": document_category,
                    "error": f"JSON parsing error on line {e.lineno}: {e.msg}",
                    "raw_response": response_text[:500] if len(response_text) > 500 else response_text
                }
        
        except Exception as e:
            return {
                "success": False,
                "category": document_category,
                "error": f"Policy check error: {str(e)}"
            }
    
    def check_multiple_documents(self, documents: list) -> list:
        """
        Check compliance for multiple documents.
        
        Args:
            documents (list): List of tuples (document_text, category)
            
        Returns:
            list: List of compliance check results
        """
        results = []
        for document_text, category in documents:
            result = self.check_compliance(document_text, category)
            results.append(result)
        
        return results
    
    def format_violations(self, compliance_result: dict) -> str:
        """
        Format compliance violations for display.
        
        Args:
            compliance_result (dict): Result from check_compliance
            
        Returns:
            str: Formatted violation display
        """
        if not compliance_result.get("success"):
            return f"Error: {compliance_result.get('error', 'Unknown error')}"
        
        data = compliance_result.get("data", {})
        violations = data.get("violations", [])
        
        if not violations:
            return "✅ No policy violations found"
        
        output = f"⚠️ {len(violations)} Policy Violation(s) Found:\n\n"
        
        for i, violation in enumerate(violations, 1):
            severity = violation.get("severity", "medium").upper()
            severity_emoji = {"LOW": "🟡", "MEDIUM": "🟠", "HIGH": "🔴"}.get(severity, "⚠️")
            
            output += f"{severity_emoji} **Violation {i}: {violation.get('policy_name', 'Unknown Policy')}**\n"
            output += f"   **Detail:** {violation.get('violation_detail', '')}\n"
            output += f"   **Policy Requirement:** {violation.get('policy_requirement', '')}\n"
            output += f"   **Evidence:** {violation.get('document_evidence', '')}\n"
            output += f"   **Severity:** {severity}\n\n"
        
        return output
