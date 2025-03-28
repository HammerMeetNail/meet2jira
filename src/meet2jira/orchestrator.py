import logging
import subprocess
import atexit
import os
import time
import requests
import uuid
from typing import List, Dict, Optional
from .parser import MeetingParser
from .jira_client import JiraClient
from .report_storage import ReportStorage

class Meet2JiraOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.jira_client = JiraClient()
        self.report_storage = ReportStorage()
        self.parser = None
        self.ollama_process = None
        atexit.register(self.cleanup_ollama)
        
    def check_ollama_status(self):
        """Check if Ollama service is running"""
        try:
            response = requests.get('http://localhost:11434', timeout=2)
            return response.ok
        except (requests.ConnectionError, requests.Timeout):
            return False
            
    def start_ollama(self):
        """Start Ollama service in background if not running"""
        if not self.check_ollama_status():
            self.logger.info("Starting Ollama service...")
            self.ollama_process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            # Wait for service to become available
            time.sleep(2)
            if not self.check_ollama_status():
                raise RuntimeError("Failed to start Ollama service")
                
    def cleanup_ollama(self):
        """Clean up Ollama process on exit"""
        if self.ollama_process:
            self.logger.info("Stopping Ollama service...")
            self.ollama_process.terminate()
            try:
                self.ollama_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ollama_process.kill()

    def generate_status_report(self, jql: str, model: str = 'llama2') -> dict:
        """Generate a status report from Jira issues matching the JQL"""
        self.start_ollama()
        self.parser = MeetingParser(model=model)
        
        # Get current issues from Jira
        issues = self.jira_client.get_issues_by_jql(jql)
        if not issues:
            return {"error": "No issues found matching the JQL query"}
            
        # Get previous report for comparison
        previous_report = self.report_storage.get_previous_report(jql)
        
        # Generate report ID and save current state
        report_id = str(uuid.uuid4())
        self.report_storage.save_report(report_id, jql, issues)
        
        # Prepare context for LLM
        report_context = {
            'current_issues': [
                {
                    'key': issue['key'],
                    'status': issue['fields']['status']['name'],
                    'assignee': issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
                    'summary': issue['fields']['summary'],
                    'priority': issue['fields']['priority']['name'],
                    'created': issue['fields']['created'],
                    'updated': issue['fields']['updated']
                }
                for issue in issues
            ],
            'previous_report': previous_report['issues'] if previous_report else None
        }
        
        # Generate summary using LLM
        summary = self.parser.generate_report_summary(report_context, model=model)
        
        return {
            'report_id': report_id,
            'jql': jql,
            'issue_count': len(issues),
            'summary': summary,
            'previous_report': previous_report
        }

    def process_transcript(self, transcript: str, model: str = 'llama2', dry_run: bool = False) -> tuple[List[Dict], str]:
        """Process meeting transcript and create Jira issues"""
        self.start_ollama()
        self.parser = MeetingParser(model=model)
        self.logger.info("Processing meeting transcript")
        
        # Parse transcript into actionable items
        parsed_issues = self.parser.parse(transcript, model=model)
        
        # Create Jira issues for each actionable item
        created_issues = []
        for issue in parsed_issues['issues']:
            if dry_run:
                created_issues.append(issue)
            else:
                # Show issue details and prompt for approval
                print(f"\nProposed Jira Issue:")
                print(f"Title: {issue['title']}")
                print(f"Type: {issue['type']}")
                print(f"Priority: {issue['priority']}")
                print(f"Labels: {', '.join(issue['labels'])}")
                print(f"Description:\n{issue['description']}\n")
                
                response = input("Create this issue? (y/n): ").strip().lower()
                if response == 'y':
                    try:
                        result = self.jira_client.create_issue(issue)
                        created_issues.append(result)
                        self.logger.info(f"Created issue: {result['key']}")
                    except Exception as e:
                        self.logger.error(f"Failed to create issue: {str(e)}")
                        continue
                else:
                    self.logger.info(f"Skipped creating issue: {issue['title']}")
                    continue
                
        return created_issues, ""
