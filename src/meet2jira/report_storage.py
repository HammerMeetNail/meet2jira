import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path

class ReportStorage:
    def __init__(self, db_path: str = "meet2jira_reports.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    jql_filter TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_issues (
                    report_id TEXT,
                    issue_key TEXT,
                    status TEXT NOT NULL,
                    assignee TEXT,
                    summary TEXT,
                    PRIMARY KEY (report_id, issue_key),
                    FOREIGN KEY (report_id) REFERENCES reports(report_id)
                )
            """)
            conn.commit()

    def save_report(self, report_id: str, jql: str, issues: List[dict]):
        """Save a report and its issues to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Save report metadata
            cursor.execute(
                "INSERT INTO reports VALUES (?, ?, ?)",
                (report_id, jql, datetime.utcnow())
            )
            
            # Save all issues
            for issue in issues:
                cursor.execute(
                    "INSERT INTO report_issues VALUES (?, ?, ?, ?, ?)",
                    (
                        report_id,
                        issue['key'],
                        issue['fields']['status']['name'],
                        issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else None,
                        issue['fields']['summary']
                    )
                )
            conn.commit()

    def get_previous_report(self, jql: str) -> Optional[dict]:
        """Get the most recent report matching the given JQL filter"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get most recent report matching this JQL
            cursor.execute("""
                SELECT * FROM reports 
                WHERE jql_filter = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (jql,))
            report = cursor.fetchone()
            
            if not report:
                return None
                
            # Get all issues for this report
            cursor.execute("""
                SELECT * FROM report_issues
                WHERE report_id = ?
            """, (report['report_id'],))
            issues = cursor.fetchall()
            
            return {
                'report_id': report['report_id'],
                'jql_filter': report['jql_filter'],
                'created_at': report['created_at'],
                'issues': [dict(issue) for issue in issues]
            }
