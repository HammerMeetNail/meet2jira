import os
import logging
from typing import List
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

    def get_issues_by_jql(self, jql: str, max_results: int = 100) -> List[dict]:
        """Execute JQL query and return paginated results"""
        self.logger.info(f"Executing JQL query: {jql}")
        
        issues = []
        start_at = 0
        
        while True:
            results = self.client.jql(
                jql, 
                start=start_at, 
                limit=min(50, max_results - start_at))
            
            issues.extend(results['issues'])
            start_at += len(results['issues'])
            
            if start_at >= results['total'] or start_at >= max_results:
                break
                
        return issues
