# Meet2Jira

A Python application that processes meeting transcripts and creates corresponding Jira issues.

## Features

- Processes meeting transcripts from text files
- Extracts actionable items using LLM
- Creates Jira issues with proper formatting
- Configurable through environment variables

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure with your credentials
4. Place your LLM model file in the configured location

## Usage

```bash
python -m meet2jira.cli path/to/transcript.txt
```

## Configuration

Edit `config/settings.yaml` to customize:
- Jira field mappings
- Default issue types
- LLM parameters

## Testing

Run tests with:
```bash
pytest
