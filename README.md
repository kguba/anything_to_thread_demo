# Anything to Thread

Convert YouTube videos into engaging X (Twitter) threads with AI. This tool uses OpenAI's GPT-4 to analyze video transcripts and create viral-worthy threads.

## Features

- YouTube video URL input
- Automatic transcript extraction
- AI-powered summary generation
- Thread creation with proper formatting
- Progress tracking and time estimation
- Download option for summary and thread

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/anything-to-thread.git
cd anything-to-thread
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
streamlit run main.py
```

## Usage

1. Enter your OpenAI API key
2. Paste a YouTube video URL
3. Click "Submit"
4. Wait for the processing to complete
5. View and download the generated summary and thread

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for YouTube video access

## License

MIT License
