import ollama

def list_models():
    """List available Ollama models with detailed information."""
    try:
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
    except Exception as e:
        print(f"Error listing models: {str(e)}")
