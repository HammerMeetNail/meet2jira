import json
import pytest
from unittest.mock import patch, MagicMock, ANY
from meet2jira.parser import MeetingParser

class TestMeetingParser:
    @pytest.fixture
    def mock_ollama(self):
        with patch('meet2jira.parser.ollama') as mock:
            yield mock

    def test_parse_success(self, mock_ollama):
        """Test successful parsing of meeting transcript"""
        mock_ollama.generate.return_value = {
            'response': json.dumps({
                'issues': [{
                    'title': 'Test issue',
                    'type': 'Task', 
                    'priority': 'Major',
                    'labels': ['test'],
                    'description': 'Test description'
                }],
                'raw_response': 'test raw response'
            })
        }

        parser = MeetingParser(model='test-model')
        transcript = "Test meeting transcript"
        result = parser.parse(transcript)

        mock_ollama.generate.assert_called_once_with(
            model='test-model',
            prompt=ANY,
            options={'num_ctx': 24576},
            format='json'
        )
        assert len(result['issues']) == 1
        assert result['issues'][0]['title'] == 'Test issue'
        assert result['raw_response'] == {
            'issues': [{
                'title': 'Test issue',
                'type': 'Task',
                'priority': 'Major',
                'labels': ['test'],
                'description': 'Test description'
            }],
            'raw_response': 'test raw response'
        }

    def test_parse_empty_transcript(self, mock_ollama):
        """Test parsing empty transcript"""
        parser = MeetingParser(model='test-model')
        with pytest.raises(ValueError, match='Transcript cannot be empty'):
            parser.parse('')
        mock_ollama.generate.assert_not_called()

    def test_parse_invalid_response(self, mock_ollama):
        """Test parsing invalid LLM response"""
        mock_ollama.generate.return_value = {
            'response': 'invalid json'
        }

        parser = MeetingParser(model='test-model')
        with pytest.raises(ValueError, match='Invalid response format'):
            parser.parse('Test transcript')

    def test_parse_llm_error(self, mock_ollama):
        """Test LLM generation error"""
        mock_ollama.generate.side_effect = Exception('LLM error')

        parser = MeetingParser(model='test-model')
        with pytest.raises(Exception, match='LLM error'):
            parser.parse('Test transcript')
