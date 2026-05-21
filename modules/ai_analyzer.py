from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from .prompt_loader import load_prompt

load_dotenv()


class LoanAnalyzer:
    """A class to analyze loan applications using LangChain and OpenRouter."""
    
    def __init__(self, model: str = "openrouter/auto"):
        """
        Initialize the LoanAnalyzer with OpenRouter API via ChatOpenAI.
        
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
        
        # Load prompt from external file
        prompt_template = load_prompt("prompts/loan_analysis.txt")
        self.prompt = PromptTemplate(
            input_variables=[
                "full_name",
                "date_of_birth",
                "gender",
                "monthly_income",
                "monthly_debt_payment",
                "credit_score",
                "loan_amount",
                "loan_term_months",
                "property_value",
                "employment_years"
            ],
            template=prompt_template
        )
    
    def analyze_loan(self, data: dict) -> str:
        """
        Analyze a loan application based on customer data.
        
        Args:
            data (dict): Dictionary containing:
                - full_name: Applicant's full name
                - date_of_birth: Applicant's DOB
                - gender: Applicant's gender
                - monthly_income: Monthly income
                - monthly_debt_payment: Monthly debt payments
                - credit_score: Credit score (300-850)
                - loan_amount: Requested loan amount
                - loan_term_months: Desired loan term in months
                - property_value: Property collateral value
                - employment_years: Years at current employment
        
        Returns:
            str: The analysis result from the LLM.
        """
        formatted_prompt = self.prompt.format(**data)
        response = self.llm.invoke(formatted_prompt)
        return response.content


def analyze_loan(data: dict) -> str:
    """
    Standalone function to analyze a loan application.
    
    Args:
        data (dict): Dictionary containing:
            - full_name: Applicant's full name
            - date_of_birth: Applicant's DOB
            - gender: Applicant's gender
            - monthly_income: Monthly income
            - monthly_debt_payment: Monthly debt payments
            - credit_score: Credit score (300-850)
            - loan_amount: Requested loan amount
            - loan_term_months: Desired loan term in months
            - property_value: Property collateral value
            - employment_years: Years at current employment
    
    Returns:
        str: The analysis result from the LLM.
    """
    analyzer = LoanAnalyzer()
    return analyzer.analyze_loan(data)
