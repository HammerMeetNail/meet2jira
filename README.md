# Meet2Jira

> This repository was created with help from DeepSeek-V3

A CLI tool for processing meeting transcripts into Jira issues using AI models.

## Installation

1. Install Ollama and download the model:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5-coder:7b
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/meet2jira.git
cd meet2jira
```

3. Install the package in editable mode:
```bash
pip install -e .
```

4. (Optional) Import models from LM Studio to Ollama
```bash
go install github.com/sammcj/gollama@HEAD
gollama -link-lmstudio -lm-dir /Users/$USER/.lmstudio/models
```

## Configuration

Export the following environment variables:
```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_USER=your@email.com
JIRA_API_TOKEN=your-api-token
```

## Usage

### Report Generation
Generate status reports from existing Jira issues:
```bash
meet2jira --report --jql "project = TEST AND status != Done" --model qwen2.5-coder:7b
```

The report includes:
- Summary of current issue statuses
- Count of matching issues
- Comparison with previous report (if available)
- Key changes and trends

### Basic Usage
```bash
# Dry Run does not require env variables
meet2jira --dry-run --transcript test_transcript.txt --model qwen2.5-coder:7b
```

### Report Options
- `--report`, `-r`: Generate status report from Jira issues
- `--jql`, `-j`: JQL query to filter issues for report (required with --report)

### Basic Options
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
