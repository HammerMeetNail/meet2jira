# Meet2Jira

A CLI tool for processing meeting transcripts into Jira issues using AI models.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/meet2jira.git
cd meet2jira
```

2. Install the package in editable mode:
```bash
pip install -e .
```

## Usage

### Basic Usage
```bash
meet2jira --transcript /path/to/transcript.txt
```

### Options
- `--model`, `-m`: Specify the Ollama model to use (default: llama2)
- `--dry-run`: Run without creating Jira issues
- `--verbose`, `-v`: Show detailed output including parsed transcript
- `--list-models`, `-l`: List available Ollama models
- `--transcript`, `-t`: Meeting transcript text or path to transcript file

### Examples

1. Process a transcript file:
```bash
meet2jira --transcript meeting.txt
```

2. List available models:
```bash
meet2jira --list-models
```

3. Dry run with verbose output:
```bash
meet2jira --transcript meeting.txt --dry-run --verbose
```

4. Use a specific model:
```bash
meet2jira --transcript meeting.txt --model mistral
```

## Configuration

Create a `.env` file in the project root with your Jira credentials:
```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_USER=your@email.com
JIRA_API_TOKEN=your-api-token
```

## Development

To run tests:
```bash
python -m pytest tests/
```

To run the CLI directly during development:
```bash
python -m src.meet2jira.cli --transcript test_transcript.txt
