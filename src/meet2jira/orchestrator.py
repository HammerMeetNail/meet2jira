import logging
import subprocess
import atexit
import os
import time
import requests
from typing import List, Dict
from .parser import MeetingParser
from .jira_client import JiraClient

class Meet2JiraOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.jira_client = JiraClient()
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
                
        return created_issues, parsed_issues['raw_response']
