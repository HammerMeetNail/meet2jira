import argparse
import logging
from .orchestrator import Meet2JiraOrchestrator
from .models import list_models

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process meeting transcripts into Jira issues')
    parser.add_argument('--model', '-m', help='Ollama model to use for processing', default='llama2')
    parser.add_argument('--dry-run', action='store_true', help='Run without creating Jira issues')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output including parsed transcript')
    parser.add_argument('--list-models', '-l', action='store_true', help='List available Ollama models')
    parser.add_argument('--transcript', '-t', required=False, help='Meeting transcript text or path to transcript file')
    parser.add_argument('--report', '-r', action='store_true', help='Generate status report from Jira issues')
    parser.add_argument('--jql', '-j', required=False, help='JQL query for report generation')
    args = parser.parse_args()

    # Validate arguments
    if not args.list_models and not args.transcript and not args.report:
        parser.error('Either --transcript, --report, or --list-models is required')
    if args.report and not args.jql:
        parser.error('--jql is required when generating reports')

    # List models if requested
    if args.list_models:
        list_models()
        return

    # Get transcript content if not in report mode
    transcript = None
    if not args.report:
        try:
            with open(args.transcript, 'r') as f:
                transcript = f.read()
        except (IOError, OSError):
            # If not a valid file path, treat as direct text
            transcript = args.transcript

    # Process request
    orchestrator = Meet2JiraOrchestrator()
    
    if args.report:
        report = orchestrator.generate_status_report(args.jql, model=args.model)
        print("\nStatus Report:")
        print("-" * 40)
        print(report['summary'])
        print("-" * 40)
        print(f"\nGenerated from {report['issue_count']} issues matching JQL: {report['jql']}")
        return
    else:
        results, llm_response = orchestrator.process_transcript(transcript, model=args.model, dry_run=args.dry_run)

    if args.verbose:
        print("\nParsed Transcript:")
        print("-" * 40)
        print(transcript)
        print("-" * 40)
        print("\nLLM Response:")
        print("-" * 40)
        try:
            import json
            print(json.dumps(llm_response, indent=2))
        except json.JSONDecodeError:
            print(llm_response)
        print("-" * 40)
        print()
    
    # Output results
    if args.dry_run:
        print(f"Would create {len(results)} Jira issues:")
        for result in results:
            print(f"- Title: {result['title']}")
            print(f"  Type: {result['type']}")
            print(f"  Priority: {result['priority']}")
            print(f"  Labels: {', '.join(result['labels'])}")
            print(f"  Description:\n{result['description']}\n")
            print("-" * 40)
    else:
        print(f"Created {len(results)} Jira issues:")
        for result in results:
            print(f"- {result['key']}: {result['self']}")

if __name__ == "__main__":
    main()
