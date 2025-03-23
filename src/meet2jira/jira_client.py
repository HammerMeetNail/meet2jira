import os
import logging
from atlassian import Jira

class JiraClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = Jira(
            url=os.getenv('JIRA_URL'),
            token=os.getenv('JIRA_PAT')
        )

    def create_issue(self, issue_data: dict) -> dict:
        """Create a Jira issue from parsed meeting data"""
        self.logger.info(f"Creating Jira issue: {issue_data['title']}")
        
        fields = {
            "project": {"key": os.getenv('JIRA_PROJECT_KEY')},
            "summary": issue_data['title'],
            "description": issue_data['description'],
            "issuetype": {"name": issue_data['type']},
            "priority": {"name": issue_data['priority']},
            "labels": issue_data['labels']
        }

        return self.client.issue_create(fields=fields)
