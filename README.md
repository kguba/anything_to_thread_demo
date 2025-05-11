# 🧵 Anything To Thread

Convert YouTube videos into engaging Twitter/X threads with AI. This tool automatically generates well-structured, informative threads from any YouTube video with captions.

## ✨ Features

- 🎥 Convert YouTube videos to Twitter/X threads
- 🌍 Support for multiple languages (English, German, Spanish)
- 🤖 Powered by gpt-4o-mini for high-quality content and cost efficiency
- 📝 Automatic thread structuring and formatting
- 🔒 Secure API key handling with session-based storage
- 🎯 Smart request limiting system
- 🎨 Clean and intuitive user interface
- 📱 Responsive tweet display with automatic height adjustment

## 🚀 Live Demo

Try it out: [Anything To Thread](https://anything-to-thread.streamlit.app)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/kguba/anything_to_thread.git
cd anything_to_thread
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux:
python -m venv .venv
source .venv/bin/activate

# On Windows:
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the Streamlit configuration:
```bash
# Create .streamlit directory
mkdir .streamlit

# Create secrets.toml file (this will be empty, API key will be entered in the app)
touch .streamlit/secrets.toml
```

## 🎮 Usage

1. Start the application:
```bash
streamlit run main.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter your OpenAI API key:
   - The key will be securely stored in your session
   - You'll need to re-enter it if you restart the app
   - Your key is never stored permanently

4. Enter a YouTube URL:
   - The URL must be a valid YouTube video
   - The video must have captions available
   - The URL should be in the format: `https://www.youtube.com/watch?v=...` or `https://youtu.be/...`

5. Select your preferred language:
   - 🇺🇸 English
   - 🇩🇪 German
   - 🇪🇸 Spanish

6. Click "Submit" and wait for the magic to happen!

## 🔒 Security Features

- API keys are stored securely in session state
- No persistent storage of sensitive data
- Input validation and sanitization
- No sensitive data is logged
- Automatic session expiration
- Secure password field for API key input

## ⚠️ Limitations

- Maximum 5 requests per user
- Requires YouTube videos with available captions
- OpenAI API key required for usage
- API key needs to be re-entered after session expiration

## 🛠️ Technical Stack

- Python 3.9+
- Streamlit
- LangChain
- OpenAI gpt-4o-mini
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

- OpenAI for providing the gpt-4o-mini API
- Streamlit for the amazing web framework
- All contributors and users of this project
