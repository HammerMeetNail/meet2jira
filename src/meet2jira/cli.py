import argparse
import logging
from .orchestrator import Meet2JiraOrchestrator

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process meeting transcripts into Jira issues')
    parser.add_argument('--model', '-m', help='Ollama model to use for processing', default='llama2')
    parser.add_argument('--dry-run', action='store_true', help='Run without creating Jira issues')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output including parsed transcript')
    parser.add_argument('--list-models', '-l', action='store_true', help='List available Ollama models')
    args = parser.parse_args()

    # Add transcript argument after parsing args
    parser.add_argument('--transcript', '-t', required=not args.list_models, help='Meeting transcript text or path to transcript file')
    args = parser.parse_args()

    # List models if requested
    if args.list_models:
        try:
            import ollama
            response = ollama.list()
            print("Available Ollama models:")
            print(f"{'NAME':<50} {'ID':<15} {'SIZE':<10} {'MODIFIED':<20}")
            for model in response.get('models', []):
                modified_time = model.get('modified_at', '')
                if hasattr(modified_time, 'strftime'):
                    modified_time = modified_time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{model.get('model', 'unnamed'):<50} "
                      f"{model.get('digest', '')[:12]:<15} "
                      f"{model.get('size', 0)/1e9:.1f} GB "
                      f"{modified_time}")
            return
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return

    # Get transcript content
    # Check if transcript is a file path
    try:
        with open(args.transcript, 'r') as f:
            transcript = f.read()
    except (IOError, OSError):
        # If not a valid file path, treat as direct text
        transcript = args.transcript

    # Process transcript
    orchestrator = Meet2JiraOrchestrator()
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
