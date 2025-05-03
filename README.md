# Anything To Thread

Ein YouTube Video Summarizer, der Videos in Text zusammenfasst und automatisch virale X (Twitter) Threads erstellt.

## Setup

1. Klonen Sie das Repository:
```bash
git clone https://github.com/kguba/anything_to_thread.git
cd anything_to_thread
```

2. Erstellen Sie eine virtuelle Umgebung und aktivieren Sie sie:
```bash
python -m venv venv
source venv/bin/activate  # Für Unix/MacOS
# oder
.\venv\Scripts\activate  # Für Windows
```

3. Installieren Sie die Abhängigkeiten:
```bash
pip install -r requirements.txt
```

4. Erstellen Sie eine `.env` Datei im Hauptverzeichnis und fügen Sie Ihren OpenAI API-Key hinzu:
```
OPENAI_API_KEY=your_api_key_here
```

5. Starten Sie die App:
```bash
streamlit run main.py
```

## Sicherheit

- Der OpenAI API-Key wird aus der Umgebungsvariable geladen und ist nicht im Code gespeichert
- Die `.env` Datei ist in `.gitignore` aufgenommen und wird nicht ins Repository hochgeladen
- Stellen Sie sicher, dass Sie Ihre `.env` Datei niemals teilen oder ins Repository pushen

## Verwendung

1. Öffnen Sie die App in Ihrem Browser (normalerweise unter http://localhost:8501)
2. Fügen Sie die URL eines YouTube-Videos ein
3. Warten Sie auf die Zusammenfassung und den generierten Thread
4. Optional: Laden Sie beides als Textdatei herunter
