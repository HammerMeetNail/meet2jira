import argparse
import logging
from .orchestrator import Meet2JiraOrchestrator

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process meeting transcripts into Jira issues')
    parser.add_argument('file', help='Path to meeting transcript file')
    args = parser.parse_args()

    # Read transcript file
    with open(args.file, 'r') as f:
        transcript = f.read()

    # Process transcript
    orchestrator = Meet2JiraOrchestrator()
    results = orchestrator.process_transcript(transcript)
    
    # Output results
    print(f"Created {len(results)} Jira issues:")
    for result in results:
        print(f"- {result['key']}: {result['self']}")

if __name__ == "__main__":
    main()
