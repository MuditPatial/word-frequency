# 🔍 WordLens — Word Frequency Analyzer

> **Live Demo → [word-frequency-8gss.onrender.com](https://word-frequency-8gss.onrender.com)**

A production-ready, full-stack word frequency analyzer built with **Python & Flask**. Upload any PDF, DOCX, or TXT document and instantly get word frequency statistics, interactive charts, contextual word search, and data exports — all in a premium dark-mode dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Multi-format Upload** | Drag & drop PDF, DOCX, or TXT files (up to 16 MB) |
| 🔍 **Word Search** | Search any word and see its count + highlighted context snippets |
| 📊 **Bar Chart** | Interactive horizontal chart of top N most frequent words |
| 🔤 **Letter Frequency** | Chart of the most common letters in the document |
| 📋 **Word Table** | Ranked table with frequency percentage bars |
| 📈 **Text Statistics** | Total words, unique words, sentences, reading time, lexical density |
| ⬇️ **Export** | Download results as CSV or JSON |
| 📚 **Sample Texts** | Pre-loaded samples (Pride & Prejudice, AI News Article) |
| 🌙 **Dark Mode UI** | Premium glassmorphism design with smooth animations |

---

## 🖥️ Screenshots

### Dashboard
```
Upload → Analyze → Explore
```
- **Left panel**: File upload (drag & drop), text input, word search, export buttons
- **Right panel**: Stats row + tabbed charts (Bar / Letter / Table)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10, Flask 3.x |
| **PDF Parsing** | pdfplumber |
| **DOCX Parsing** | python-docx |
| **Charts** | Chart.js 4.x |
| **Fonts** | Inter + JetBrains Mono (Google Fonts) |
| **Production Server** | Gunicorn |
| **Hosting** | Render.com |

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/wordlens.git
cd wordlens
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the server
```bash
python run.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 📁 Project Structure

```
word-frequency-analyzer/
│
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── analyzer.py        # Core NLP analysis engine
│   ├── extractor.py       # PDF / DOCX / TXT text extractor
│   ├── routes.py          # REST API endpoints
│   └── utils.py           # Stopword list & text cleaning
│
├── static/
│   ├── css/style.css      # Premium dark-mode design system
│   ├── js/app.js          # Chart.js dashboard logic
│   └── assets/samples/    # Pre-loaded sample texts
│
├── templates/
│   └── index.html         # Main dashboard template
│
├── config.py              # App configuration
├── run.py                 # Entry point (local dev + Render)
├── requirements.txt       # Python dependencies
├── Procfile               # Render/Heroku process file
├── render.yaml            # Render blueprint config
└── .python-version        # Python 3.10.11
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/analyze` | Analyze uploaded file or raw text |
| `POST` | `/api/search` | Search a word in the last analyzed document |
| `GET` | `/api/export/json` | Download results as JSON |
| `GET` | `/api/export/csv` | Download results as CSV |
| `GET` | `/api/samples` | List available sample texts |
| `GET` | `/api/sample/<filename>` | Load a sample text |

### Example: Analyze via API
```bash
# Upload a PDF
curl -X POST https://word-frequency-8gss.onrender.com/api/analyze \
  -F "file=@document.pdf" \
  -F "top_n=20" \
  -F "remove_stopwords=true"

# Paste raw text
curl -X POST https://word-frequency-8gss.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "To be or not to be, that is the question.", "top_n": 10}'
```

### Example: Search a word
```bash
curl -X POST https://word-frequency-8gss.onrender.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"word": "love"}'
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | auto-generated | Flask session secret |
| `FLASK_DEBUG` | `false` | Enable debug mode |
| `PORT` | `5000` | Server port (auto-set by Render) |

---

## 📦 Deploy to Render

1. Fork this repo
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
5. Click **Deploy** 🎉

> ⚠️ Render free tier spins down after 15 min of inactivity. First request may take ~30s to wake up.

---

## 📄 License

MIT — free to use, modify, and distribute.

---

<p align="center">Built with ❤️ using Python & Flask</p>
