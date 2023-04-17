# Agent Smith - GPT-4 Code Generator and Self Corrector
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Objective
This Python script is a example of how to use the GPT-4 model to generate code(TODO) and self correct if there is runtime error.

The script uses OpenAI's natural language processing (NLP) capabilities to create new tasks based on the objective and generate code based on the task. 

# Dependencies
    pip install black
    pip install flake8

- Python 3.6+
- [OpenAI GPT-4](https://openai.com/blog/gpt-4/)
- Setup OpenAI API key in environment variable `OPENAI_API_KEY`

# Installation

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

# Usage
    
    python agent_smith.py buggy_script.py "subtract" 20 3 


# Special Thanks
It is inspired by [Wolverine](https://github.com/biobootloader/wolverine) for its healing abilities.