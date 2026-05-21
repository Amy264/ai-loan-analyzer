# AI Loan Analyzer

An intelligent loan analysis system that leverages AI and RAG (Retrieval-Augmented Generation) to analyze loan applications, extract relevant data, and validate against loan policies.

## Features

- **AI-Powered Analysis**: Uses advanced AI models to analyze loan applications intelligently
- **Document Processing**: Automatically extracts and parses relevant information from loan documents
- **Policy Validation**: Checks loan applications against predefined loan policies
- **Intelligent RAG**: Retrieval-Augmented Generation for context-aware responses
- **Data Extraction**: Specialized extraction for personal information, salary, credit reports, and asset valuation
- **Rule Engine**: Flexible rule-based evaluation system for policy compliance

## Project Structure

```
ai-loan-analyzer/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── setup_offline.py            # Offline setup configuration
├── PROMPT_MANAGEMENT.md        # Prompt management documentation
│
├── data/
│   └── loan_policy.txt         # Loan policy rules and criteria
│
├── documents/                  # Directory for loan documents
│
├── modules/
│   ├── ai_analyzer.py         # AI analysis engine
│   ├── data_extractor.py      # Data extraction logic
│   ├── document_parser.py     # Document parsing utilities
│   ├── policy_checker.py      # Policy validation logic
│   ├── prompt_loader.py       # Prompt loading and management
│   ├── rag_engine.py          # RAG implementation
│   └── rule_engine.py         # Rule evaluation engine
│
└── prompts/
    ├── loan_analysis.txt                    # Main loan analysis prompt
    ├── policy_check.txt                     # Policy checking prompt
    ├── rag_response.txt                     # RAG response prompt
    └── data_extraction/
        ├── asset_valuation.txt              # Asset valuation extraction prompt
        ├── credit_report.txt                # Credit report extraction prompt
        ├── personal_information.txt         # Personal info extraction prompt
        └── salary_employment.txt            # Salary/employment extraction prompt
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download the repository:
```bash
cd ai-loan-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For offline setup, run the setup script:
```bash
python setup_offline.py
```

## Usage

Run the main application:
```bash
python app.py
```

## Configuration

- **Loan Policies**: Configure policies in `data/loan_policy.txt`
- **Prompts**: Customize AI prompts in the `prompts/` directory
- **Rules**: Modify rule definitions in the rule engine module

## Key Components

### Modules

- **ai_analyzer.py**: Core AI analysis engine for processing loan applications
- **data_extractor.py**: Extracts structured data from unstructured documents
- **document_parser.py**: Parses and prepares documents for analysis
- **policy_checker.py**: Validates applications against loan policies
- **prompt_loader.py**: Manages prompt templates for AI interactions
- **rag_engine.py**: Implements Retrieval-Augmented Generation for intelligent responses
- **rule_engine.py**: Evaluates business rules for compliance checking

### Data Files

- **loan_policy.txt**: Defines loan eligibility criteria and business rules
- **Extraction Prompts**: Specialized prompts for different data extraction tasks

## Documentation

See [PROMPT_MANAGEMENT.md](PROMPT_MANAGEMENT.md) for detailed information on prompt management and configuration.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
