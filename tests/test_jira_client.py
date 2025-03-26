import pytest
from unittest.mock import patch, MagicMock
from meet2jira.jira_client import JiraClient

class TestJiraClient:
    @pytest.fixture
    def mock_jira(self):
        with patch('meet2jira.jira_client.Jira') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_create_issue(self, mock_jira):
        """Test successful issue creation"""
        with patch.dict('os.environ', {
            'JIRA_URL': 'https://test.atlassian.net',
            'JIRA_PAT': 'token',
            'JIRA_PROJECT_KEY': 'TEST'
        }):
            client = JiraClient()
            
            issue_data = {
                'title': 'Test issue',
                'type': 'Task',
                'priority': 'Major',
                'labels': ['test'],
                'description': 'Test description'
            }
            
            mock_jira.issue_create.return_value = {
                'key': 'TEST-123',
                'self': 'https://test.atlassian.net/rest/api/2/issue/TEST-123'
            }
            
            result = client.create_issue(issue_data)
            
            mock_jira.issue_create.assert_called_once_with(fields={
                'project': {'key': 'TEST'},
                'summary': 'Test issue',
                'description': 'Test description',
                'issuetype': {'name': 'Task'},
                'priority': {'name': 'Major'},
                'labels': ['test']
            })
            
            assert result == {
                'key': 'TEST-123',
                'self': 'https://test.atlassian.net/rest/api/2/issue/TEST-123'
            }

    def test_create_issue_failure(self, mock_jira):
        """Test failed issue creation"""
        with patch.dict('os.environ', {
            'JIRA_URL': 'https://test.atlassian.net',
            'JIRA_PAT': 'token',
            'JIRA_PROJECT_KEY': 'TEST'
        }):
            client = JiraClient()
            
            issue_data = {
                'title': 'Test issue',
                'type': 'Task',
                'priority': 'Major',
                'labels': ['test'],
                'description': 'Test description'
            }
            
            mock_jira.issue_create.side_effect = Exception('API error')
            
            with pytest.raises(Exception, match='API error'):
                client.create_issue(issue_data)
