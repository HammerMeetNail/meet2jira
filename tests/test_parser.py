import pytest
from meet2jira.parser import MeetingParser

class TestMeetingParser:
    @pytest.fixture
    def parser(self):
        return MeetingParser()

    def test_parse_transcript(self, parser):
        """Test basic transcript parsing"""
        transcript = "Meeting Notes:\n- [Action] Implement new feature"
        result = parser.parse(transcript)
        assert len(result['issues']) > 0
        assert 'title' in result['issues'][0]
        assert 'description' in result['issues'][0]
