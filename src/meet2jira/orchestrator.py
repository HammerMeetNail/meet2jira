import logging
from typing import List, Dict
from .parser import MeetingParser
from .jira_client import JiraClient

class Meet2JiraOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.jira_client = JiraClient()
        self.parser = None

    def process_transcript(self, transcript: str, model: str = 'llama2', dry_run: bool = False) -> tuple[List[Dict], str]:
        self.parser = MeetingParser(model=model)
        """Process meeting transcript and create Jira issues"""
        self.logger.info("Processing meeting transcript")
        
        # Parse transcript into actionable items
        parsed_issues = self.parser.parse(transcript, model=model)
        
        # Create Jira issues for each actionable item
        created_issues = []
        for issue in parsed_issues['issues']:
            if dry_run:
                created_issues.append(issue)
            else:
                try:
                    result = self.jira_client.create_issue(issue)
                    created_issues.append(result)
                    self.logger.info(f"Created issue: {result['key']}")
                except Exception as e:
                    self.logger.error(f"Failed to create issue: {str(e)}")
                    continue
                
        return created_issues, parsed_issues['raw_response']
