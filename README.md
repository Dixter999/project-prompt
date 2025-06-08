# ProjectPrompt v2.0

🤖 Analyze your project and get AI-powered suggestions for improvements.

## Quick Start

1. **Clone and Install**:
   ```bash
   git clone https://github.com/your-username/projectprompt
   cd projectprompt
   pip install -e .
   ```

2. **Configure API Keys**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key:
   # ANTHROPIC_API_KEY=your_key_here
   # OR
   # OPENAI_API_KEY=your_key_here
   ```

3. **Analyze Your Project**:
   ```bash
   projectprompt analyze /path/to/your/project
   projectprompt suggest "Core Files"
   ```

## Requirements
- Python 3.8+
- API key from [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)

## Commands
- `projectprompt analyze <path>` - Analyze project structure
- `projectprompt suggest <group>` - Get AI suggestions for a group
- `projectprompt status` - Check analysis status

## License
MIT
