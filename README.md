# 🕯️ Pantry‑Powered Date‑Night Planner

An interactive, multimodal Streamlit app that turns the ingredients you already have—typed text, PDFs, or even photos—into a fully custom, romantic date‑night plan. Powered by LangChain and Google’s Gemini model, it crafts recipes, ambient décor ideas, music suggestions, and playful icebreakers, refining its recommendations until you say “Yes, this is perfect!”

---

## ✨ Features

- **Multimodal Input**  
  - Upload pantry lists via TXT/PDF or snap a photo of ingredients.  
  - The LLM extracts and synthesizes every item into one unified list.

- **AI‑Driven Date‑Night Concierge**  
  - Suggests a main dish (and optional pantry add‑ons) with step‑by‑step instructions.  
  - Designs ambiance (lighting, music) and décor tips.  
  - Proposes a meaningful or playful icebreaker.

- **Iterative, Contextual Chat**  
  - Remembers your preferences across the session.  
  - Asks clarifying questions when needed.  
  - Lets you request tweaks—“Change the ambiance,” “Suggest a different recipe,” or declare completion.

- **Clean, Local Interface**  
  - Built in Streamlit for rapid UX.  
  - All session state lives in-browser—no external DB required.

---

## 🛠️ Tech Stack

- **LLM Orchestration:** LangChain Core  
- **Model Endpoint:** `gemini-1.5-flash` via `langchain-google-genai`  
- **Web Frontend:** Streamlit  
- **File/Text Processing:** `pypdf` (PDFs), Python stdlib (TXT), Pillow (images)  
- **Environment Management:** `python-dotenv`  

---

## 🚀 Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/<your‑username>/<repo‑name>.git
cd <repo‑name>

python3 -m venv .venv
source .venv/bin/activate     # macOS/Linux
.\.venv\Scripts\activate      # Windows PowerShell

pip install -r requirements.txt
```

> **requirements.txt** should include at least:
> ```
> streamlit
> langchain-core
> langchain-google-genai
> python-dotenv
> pypdf
> pillow
> ```

### 2. Configure Environment

Create a `.env` in your project root:
```
GOOGLE_API_KEY=your_google_api_key_here
# or other creds required by langchain-google-genai
```

### 3. Run the App

```bash
streamlit run app.py
```

Open your browser to <http://localhost:8501> and follow the prompt:

> 🔯 **AI:** “Hello! What ingredients do you have? Upload photos, text files, or PDFs!”

---

## 📁 Project Structure

```
├── app.py               # Streamlit front‑end & LangChain integration
├── file_processor.py    # TXT/PDF text extractor + image loader for multimodal LLM
├── requirements.txt     # Python dependencies
└── .env.example         # Example environment‑variable template
```

- **`app.py`**  
  - Initializes Streamlit session state, chat history, and LLM chain.  
  - Renders chat UI with “AI” 🔯 and “Human” 👤 messages.  
  - Handles user uploads, processes files, and iteratively refines the date‑night plan.

- **`file_processor.py`**  
  - `process_uploaded_files(...)` reads TXT/PDF content into one string.  
  - Packages uploaded images as raw bytes + MIME types for the Gemini model.

---

## 💡 Usage Tips

- **Only text files?** The app will automatically fall back to your prompt or file contents.  
- **Image uploads** should clearly show ingredient labels or packaging for best recognition.  
- **Iterate freely:** Click “Suggest a different recipe” or “Change the ambiance” to refine until it’s perfect.

---

## 🤝 Contributing

1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/my‑awesome‑idea`)  
3. Commit your changes (`git commit -m "Add some feature"`)  
4. Push to your branch (`git push origin feature/my‑awesome‑idea`)  
5. Open a Pull Request

Please ensure all new code includes tests where appropriate and follows the existing code style.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

Enjoy planning unforgettable date nights—one pantry at a time! ✨
