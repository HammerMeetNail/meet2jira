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

    def parse(self, transcript: str, model: str = None) -> Dict[str, Any]:
        # Use provided model or fall back to instance default
        model = model or self.model
        """Parse meeting transcript and extract actionable items using LLM"""
        self.logger.info("Parsing meeting transcript with LLM")
        
        try:
            # Generate prompt and get LLM response
            prompt = self._get_llm_prompt(transcript)
            response = ollama.generate(
                model=model,
                prompt=prompt,
                options={"num_ctx": 24576},
                format="json"
            )
            
            # Parse and return the JSON response
            parsed = json.loads(response["response"])
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
            
        except Exception as e:
            self.logger.error(f"Error parsing transcript: {str(e)}")
            return {
                "issues": [{
                    "type": "Task",
                    "title": "Error processing transcript",
                    "description": f"Failed to parse transcript: {str(e)}",
                    "priority": "High",
                    "labels": ["error"]
                }]
            }
