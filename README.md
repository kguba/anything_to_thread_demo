# 🧵 Anything To Thread

Convert YouTube videos into engaging Twitter/X threads with AI. This tool automatically generates well-structured, informative threads from any YouTube video with captions.

## ✨ Features

- 🎥 Convert YouTube videos to Twitter/X threads
- 🌍 Support for multiple languages (English, German, Spanish)
- 🤖 Powered by GPT-4 for high-quality content
- 📝 Automatic thread structuring and formatting
- 🎯 Smart request limiting system
- 🎨 Clean and intuitive user interface

## 🚀 Live Demo

Try it out: [Anything To Thread](https://anything-to-thread.streamlit.app)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Anything_to_thread.git
cd Anything_to_thread
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## 🎮 Usage

1. Run the Streamlit app:
```bash
streamlit run main.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter a YouTube URL and let the magic happen!

## 🔒 Security

- API keys are stored securely in environment variables
- Request limiting system prevents abuse
- Input validation and sanitization
- No sensitive data is stored or logged

## ⚠️ Limitations

- Maximum 5 requests per user
- Requires YouTube videos with available captions
- OpenAI API key required for extended usage

## 🛠️ Technical Stack

- Python 3.9+
- Streamlit
- LangChain
- OpenAI GPT-4
- YouTube Transcript API

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ☕ Support

If you find this tool helpful, consider buying me a coffee:

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/kguba)

## 📞 Contact

For any questions or suggestions, feel free to open an issue or reach out to me directly.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 API
- Streamlit for the amazing web framework
- All contributors and users of this project
