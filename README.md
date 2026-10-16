# AI ResearchFlow — Multi-Agent Research Automation
AI ResearchFlow is a Python project that automates basic research using multiple AI agents. It accepts a research topic, generates research questions, searches the web, and creates a structured research report.

## Features
- **Research Planner Agent:** Generates five research questions based on the selected topic.
- **Researcher Agent:** Searches the web and collects source URLs and text snippets.
- **Report Writer Agent:** Creates a report containing an executive summary, key findings, challenges, conclusion, and sources.
- **Streamlit Interface:** Provides a simple web interface for submitting topics and viewing results.
- **Report Download:** Allows users to download the generated report in Markdown format.

## Technologies Used
- Python
- LangGraph
- OpenRouter
- LangChain OpenAI integration
- DuckDuckGo Search (`ddgs`)
- Streamlit
- python-dotenv

## Project Structure
```text
Multi-Agent Research Automation/
├── workflow.py
├── stream.py
├── requirements.txt
├── README.md
├── .gitignore
```

## Setup and Installation

### 1. Clone the repository
```bash

git clone https://github.com/YOUR_USERNAME/Multi-Agent-Research-Automation.git
cd Multi-Agent-Research-Automation

```

### 2. Create a virtual environment
```bash
python -m venv .myenv
```

### 3. Activate the environment
Windows PowerShell:

```powershell
.\.myenv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 5. Configure the API key
Create a `.env` file in the project root and add your own OpenRouter API key:

```text
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 6. Run the Streamlit application
```bash
python -m streamlit run stream.py
```

### Optional: Run the terminal workflow
```bash
python workflow.py
```

## How It Works
1. The user enters a research topic.
2. The Research Planner generates research questions.
3. The Researcher searches for relevant web results.
4. The Report Writer produces a structured report.
5. Streamlit displays the results and provides a Markdown download.

## Limitations
- Search results depend on the availability and quality of web search results.
- The report may contain incomplete or insufficiently supported information.
- Generated content and source links should be reviewed before relying on the report.

## Future Improvements
- Improve source relevance and research coverage.
- Add source verification and stronger evidence-grounding.
- Improve report quality and error handling.
- Add research history and report export options.

## Security
Do not commit API keys, `.env` files, virtual environments, or other secrets to version control.

## Author
Created by Sana.

AI ResearchFlow is a project focused on exploring multi-agent AI workflows and automating research using LangGraph, OpenRouter, and Streamlit.

## License
No license has been selected yet. Add a license before granting others permission to reuse or distribute this project.