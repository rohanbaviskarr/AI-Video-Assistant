# 🎥 AI Video Assistant

An AI-powered meeting intelligence assistant that transcribes meetings from YouTube videos or uploaded audio/video files, generates concise summaries, extracts actionable insights, and enables conversational Q&A using Retrieval-Augmented Generation (RAG).

Built using modern Generative AI technologies including Whisper, Sarvam AI, LangChain LCEL, Mistral AI, ChromaDB, HuggingFace Embeddings, and Streamlit.

---

## 🚀 Features

- 🎥 Process YouTube videos directly
- 📁 Upload audio or video meeting recordings
- 📝 English transcription using OpenAI Whisper (Local)
- 🌏 Hindi & Hinglish transcription using Sarvam AI
- 📋 AI-generated meeting summaries
- ✅ Automatic Action Item extraction
- 👤 Detects owners for each action item
- 📅 Extracts deadlines (when mentioned)
- 💡 Extracts Key Decisions
- ❓ Finds Open Questions & Follow-ups
- 💬 Chat with your meeting using RAG
- 🔍 Semantic Search with ChromaDB
- 📄 Export reports as PDF or TXT

---

# 🏗️ Architecture

```text
                Video / Audio / YouTube URL
                          │
                          ▼
                  Audio Extraction
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
 Whisper (English)                  Sarvam AI
                                    (Hindi/Hinglish)
        │                                   │
        └──────────────┬────────────────────┘
                       ▼
                 Transcript Generated
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
   Mistral AI                   ChromaDB
 Summary & Insights             Vector Store
         │                           │
         └─────────────┬─────────────┘
                       ▼
                 LangChain LCEL
                       │
                       ▼
                Streamlit Interface
```

---

# 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| UI | Streamlit |
| LLM | Mistral AI |
| English Transcription | OpenAI Whisper |
| Hindi/Hinglish | Sarvam AI |
| Framework | LangChain LCEL |
| Vector Database | ChromaDB |
| Embeddings | HuggingFace |
| PDF Export | ReportLab |

---

# 📂 Project Structure

```
AI-Video-Assistant/
│
├── core/
│   ├── transcription.py
│   ├── summarizer.py
│   ├── rag.py
│   └── ...
│
├── utils/
│
├── app.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/rohanbaviskarr/AI-Video-Assistant.git
```

Move into the project

```bash
cd AI-Video-Assistant
```

Create virtual environment

```bash
python -m venv .venv
```

Activate virtual environment

Windows

```bash
.venv\Scripts\activate
```

Mac/Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
MISTRAL_API_KEY=your_api_key

SARVAM_API_KEY=your_api_key
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

---

# 💬 Chat with your Meeting

After transcription:

- Ask questions about the meeting
- Retrieve discussion context
- Generate intelligent answers using RAG

Example:

> What decisions were made?

> What are the pending action items?

> Who owns Task 2?

---

# 📄 Export Options

Generate reports as:

- PDF
- TXT

---

# 📸 Screenshots

Add screenshots here after deployment.

Example:

```
Home Page

Upload Screen

Summary

Chat Interface

Export Report
```

---

# 🚀 Future Improvements

- Speaker Diarization
- Live Meeting Support
- Multi-language Translation
- Email Summary
- Google Drive Integration
- Zoom Integration
- Microsoft Teams Integration
- Meeting Analytics Dashboard

---

# 🤝 Contributing

Contributions are welcome!

Fork the repository and create a pull request.

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Rohan Baviskar**

GitHub

https://github.com/rohanbaviskarr