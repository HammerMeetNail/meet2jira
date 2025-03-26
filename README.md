# Meet2Jira

> This repository was created with help from DeepSeek-V3

A CLI tool for processing meeting transcripts into Jira issues using AI models.

## Installation

1. Install Ollama and download the model:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull granite-3.2-8b-instruct-q8_0:latest
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/meet2jira.git
cd meet2jira
```

2. Install the package in editable mode:
```bash
pip install -e .
```

## Configuration

Export the following environment variables:
```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_USER=your@email.com
JIRA_API_TOKEN=your-api-token
```

## Usage

### Basic Usage
```bash
# Dry Run does not require env variables
meet2jira --dry-run --transcript test_transcript.txt --model granite-3.2-8b-instruct-q8_0:latest
```

### Options
- `--model`, `-m`: Specify the Ollama model to use (default: llama2)
- `--dry-run`: Run without creating Jira issues
- `--verbose`, `-v`: Show detailed output including parsed transcript
- `--list-models`, `-l`: List available Ollama models
- `--transcript`, `-t`: Meeting transcript text or path to transcript file

## Development

To run tests:
```bash
python -m pytest tests/
```

To run the CLI directly during development:
```bash
python -m src.meet2jira.cli --transcript test_transcript.txt
