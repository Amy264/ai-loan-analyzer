"""
Prompt Loader Utility
Loads prompts from external template files.
"""

import os


def load_prompt(prompt_file: str) -> str:
    """
    Load prompt template from file.
    
    Args:
        prompt_file (str): Path to the prompt file relative to project root
        
    Returns:
        str: Prompt template content
    """
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(project_root, prompt_file)
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    except Exception as e:
        raise Exception(f"Error loading prompt file {prompt_file}: {str(e)}")
