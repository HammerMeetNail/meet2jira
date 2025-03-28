import logging
import ollama
import json
from typing import Dict, Any

class MeetingParser:
    def __init__(self, model: str = 'llama2'):
        self.logger = logging.getLogger(__name__)
        self.model = model
        
    def _get_llm_prompt(self, transcript: str) -> str:
        """Generate the LLM prompt using the system prompt template"""
        with open("prompts/system_prompt.txt") as f:
            system_prompt = f.read()
        return f"{system_prompt}\n\nMeeting Transcript:\n{transcript}"

    def _get_report_prompt(self, context: Dict[str, Any]) -> str:
        """Generate the LLM prompt for report generation"""
        with open("prompts/report_prompt.txt") as f:
            report_prompt = f.read()
        
        return report_prompt.format(
            current_issues=json.dumps(context['current_issues'], indent=2),
            previous_report=json.dumps(context['previous_report'], indent=2) if context['previous_report'] else "No previous report available"
        )

    def generate_report_summary(self, context: Dict[str, Any], model: str = None) -> str:
        """Generate a status report summary from Jira issues using LLM"""
        model = model or self.model
        self.logger.info("Generating status report with LLM")
        
        # Generate prompt and get LLM response
        prompt = self._get_report_prompt(context)
        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={"num_ctx": 24576}
        )
        
        return response["response"].strip()

    def parse(self, transcript: str, model: str = None) -> Dict[str, Any]:
        """Parse meeting transcript and extract actionable items using LLM"""
        if not transcript.strip():
            raise ValueError("Transcript cannot be empty")
            
        # Use provided model or fall back to instance default
        model = model or self.model
        self.logger.info("Parsing meeting transcript with LLM")
        
        # Generate prompt and get LLM response
        prompt = self._get_llm_prompt(transcript)
        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={"num_ctx": 24576},
            format="json"
        )
        
        # Parse and return the JSON response
        try:
            parsed = json.loads(response["response"])
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing transcript: {str(e)}")
            raise ValueError("Invalid response format") from e
            
        # Ensure proper JSON structure and formatting
        return {
            "issues": [
                {
                    "type": issue.get("type", "Task"),
                    "title": issue.get("title", ""),
                    "description": issue.get("description", ""),
                    "priority": issue.get("priority", "Medium"),
                    "labels": issue.get("labels", [])
                }
                for issue in parsed.get("issues", [])
            ],
            "raw_response": parsed
        }
