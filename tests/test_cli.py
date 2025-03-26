import pytest
from unittest.mock import patch, MagicMock
from meet2jira.cli import main

class TestCLI:
    @pytest.fixture
    def mock_orchestrator(self):
        with patch('meet2jira.cli.Meet2JiraOrchestrator') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            mock_instance.process_transcript.return_value = ([{
                'title': 'Test issue',
                'type': 'Task',
                'priority': 'Major',
                'labels': ['test'],
                'description': 'Test description',
                'key': 'TEST-123',
                'self': 'https://example.com/issue/TEST-123'
            }], 'llm-response')
            yield mock_instance

    def test_cli_with_transcript_file(self, mock_orchestrator, capsys):
        """Test CLI with transcript file argument"""
        test_args = ['meet2jira', '--transcript', 'test_transcript.txt', '--model', 'test-model']
        with patch('sys.argv', test_args), \
             patch('builtins.open', MagicMock(return_value=MagicMock(read=MagicMock(return_value='test content')))):
            main()
        
        # Verify the call happened with expected arguments
        mock_orchestrator.process_transcript.assert_called_once()
        args, kwargs = mock_orchestrator.process_transcript.call_args
        assert len(args) == 1  # Should have one positional argument (file object)
        assert isinstance(args[0], MagicMock)  # Verify file object was passed
        assert kwargs == {'model': 'test-model', 'dry_run': False}
        captured = capsys.readouterr()
        assert 'Created 1 Jira issues:' in captured.out
        assert 'TEST-123: https://example.com/issue/TEST-123' in captured.out

    def test_cli_with_direct_text(self, mock_orchestrator, capsys):
        """Test CLI with direct transcript text"""
        test_args = ['meet2jira', '--transcript', 'direct text', '--model', 'test-model']
        with patch('sys.argv', test_args):
            main()
        
        mock_orchestrator.process_transcript.assert_called_once_with(
            'direct text',
            model='test-model',
            dry_run=False
        )

    def test_cli_missing_arguments(self, capsys):
        """Test CLI with missing required arguments"""
        test_args = ['meet2jira']
        with patch('sys.argv', test_args), pytest.raises(SystemExit):
            main()
        
        captured = capsys.readouterr()
        assert '--transcript is required unless --list-models is specified' in captured.err

    def test_cli_dry_run(self, mock_orchestrator, capsys):
        """Test CLI dry run mode"""
        test_args = ['meet2jira', '--transcript', 'test.txt', '--model', 'test-model', '--dry-run']
        with patch('sys.argv', test_args), \
             patch('builtins.open', MagicMock(return_value=MagicMock(read=MagicMock(return_value='test content')))):
            main()
        
        # Verify the call happened with expected arguments
        mock_orchestrator.process_transcript.assert_called_once()
        args, kwargs = mock_orchestrator.process_transcript.call_args
        assert len(args) == 1  # Should have one positional argument (file object)
        assert isinstance(args[0], MagicMock)  # Verify file object was passed
        assert kwargs == {'model': 'test-model', 'dry_run': True}
        captured = capsys.readouterr()
        assert 'Would create 1 Jira issues:' in captured.out
        assert 'Title: Test issue' in captured.out
        assert 'Type: Task' in captured.out
        assert 'Priority: Major' in captured.out
        assert 'Labels: test' in captured.out
        assert 'Description:\nTest description' in captured.out
