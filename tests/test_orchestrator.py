import pytest
from unittest.mock import patch, MagicMock, call
from meet2jira.orchestrator import Meet2JiraOrchestrator

class TestMeet2JiraOrchestrator:
    @pytest.fixture
    def mock_parser(self):
        with patch('meet2jira.orchestrator.MeetingParser') as mock:
            yield mock

    @pytest.fixture
    def mock_jira(self):
        with patch('meet2jira.orchestrator.JiraClient') as mock:
            yield mock

    @pytest.fixture
    def mock_ollama(self):
        with patch('subprocess.Popen') as mock:
            mock.return_value = MagicMock()
            yield mock

    @pytest.fixture
    def mock_requests(self):
        with patch('requests.get') as mock:
            yield mock

    @pytest.fixture
    def mock_time(self):
        with patch('time.sleep') as mock:
            yield mock

    def test_process_transcript_success(self, mock_parser, mock_jira, mock_ollama, mock_requests, mock_time):
        """Test successful processing of transcript"""
        # Mock Ollama status check to return True
        mock_requests.return_value.ok = True

        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'issues': [{
                'title': 'Test issue',
                'type': 'Task',
                'priority': 'Major',
                'labels': ['test'],
                'description': 'Test description'
            }],
            'raw_response': ''
        }
        mock_parser.return_value = mock_parser_instance

        mock_jira_instance = MagicMock()
        mock_jira_instance.create_issue.return_value = {'key': 'TEST-123'}
        mock_jira.return_value = mock_jira_instance

        with patch('builtins.input', return_value='y'):
            orchestrator = Meet2JiraOrchestrator()
            transcript = "Test meeting transcript"
            issues, _ = orchestrator.process_transcript(transcript, model='test-model')

            # Verify Ollama service was checked but not started
            mock_requests.assert_called_once_with('http://localhost:11434', timeout=2)
            mock_ollama.assert_not_called()

            assert len(issues) == 1
            assert issues[0]['key'] == 'TEST-123'

    def test_process_transcript_dry_run(self, mock_parser, mock_jira):
        """Test dry run mode"""
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'issues': [{
                'title': 'Test issue',
                'type': 'Task',
                'priority': 'Major',
                'labels': ['test'],
                'description': 'Test description'
            }],
            'raw_response': ''
        }
        mock_parser.return_value = mock_parser_instance

        orchestrator = Meet2JiraOrchestrator()
        issues, _ = orchestrator.process_transcript(
            "Test transcript",
            model='test-model',
            dry_run=True
        )

        assert len(issues) == 1
        assert issues[0]['title'] == 'Test issue'
        mock_jira.create_issue.assert_not_called()

    def test_process_empty_transcript(self, mock_parser):
        """Test empty transcript handling"""
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = ValueError('Empty transcript')
        mock_parser.return_value = mock_parser_instance

        orchestrator = Meet2JiraOrchestrator()
        with pytest.raises(ValueError, match='Empty transcript'):
            orchestrator.process_transcript('', model='test-model')

    def test_ollama_start_failure(self, mock_ollama):
        """Test Ollama service start failure"""
        mock_ollama.return_value = MagicMock()
        orchestrator = Meet2JiraOrchestrator()
        with patch('meet2jira.orchestrator.requests.get') as mock_get:
            mock_get.return_value.ok = False
            with pytest.raises(RuntimeError, match='Failed to start Ollama service'):
                orchestrator.start_ollama()
