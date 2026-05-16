# Laptop Store RAG Chatbot

An intelligent, context-aware customer support chatbot for a laptop store, powered by **Retrieval-Augmented Generation (RAG)**. The project integrates state-of-the-art NLP models, a vector database, and semantic routing to seamlessly handle both product-related queries and casual chitchat.

## 🌟 Features

- **Retrieval-Augmented Generation (RAG):** Retrieves accurate product specifications and documents before generating responses using LLMs.
- **Semantic Routing:** Automatically classifies user intents to route queries to either a casual conversational agent (`chitchat`) or the RAG pipeline.
- **Contextual Awareness:** Remembers past conversation history (stored via Supabase) and resolves contextual pronouns (e.g., "it", "this laptop") to provide continuous and natural conversations.
- **Multi-LLM Support:** Compatible with OpenAI and Google GenAI models.
- **Vector Search Engine:** Uses **Qdrant** for lightning-fast semantic search.
- **Robust Evaluation:** Built-in evaluation pipeline using **Ragas** to measure Faithfulness, Answer Relevancy, Context Precision, and Answer Correctness.
- **Modern User Interface:** Interactive chat UI built with **Streamlit**.
- **RESTful API:** Exposes chatbot functionalities via a fast, asynchronous **FastAPI** backend.
- **Containerized:** Fully containerized with **Docker** and **Docker Compose** for easy local development and production deployment.

## 🛠️ Technology Stack

- **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Frontend UI:** [Streamlit](https://streamlit.io/)
- **Vector Database:** [Qdrant](https://qdrant.tech/)
- **LLM Providers:** OpenAI, Google GenAI
- **Database / History Storage:** [Supabase](https://supabase.com/)
- **Evaluation:** [Ragas](https://docs.ragas.io/), Hugging Face Datasets
- **Testing:** Pytest
- **Package Management:** `uv`
- **Containerization:** Docker & Docker Compose

## 📁 Project Structure

```text
.
├── api/                # FastAPI application routes and schemas
├── core/               # Core utilities, history management, logger, models
├── data/               # Raw and processed data for the laptop store
├── embedding/          # Embedding extraction and model configurations
├── evaluation/         # Ragas evaluation scripts (run_eval.py)
├── ingestion/          # Scripts to ingest data into Qdrant
├── llm/                # LLM text generation and query contextualization
├── qdrant_data/        # Qdrant local storage volume
├── retriever/          # Semantic routing and knowledge retrieval logic
├── tests/              # Pytest unit and integration tests
├── ui/                 # Streamlit user interface (chat.py)
├── chatbot.py          # Main Chatbot class and pipeline orchestration
├── chitchat.py         # Static/LLM chitchat handling logic
├── docker-compose.yml  # Docker Compose configuration
├── pyproject.toml      # Project dependencies and configurations
└── README.md           # Project documentation
```

## ⚙️ Prerequisites

- **Python:** >= 3.12
- **Docker & Docker Compose** (for containerized deployment)
- API Keys for OpenAI/Google GenAI and Supabase

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/nuroqzavitex/RAG_laptop_store.git
cd RAG_laptop_store
```

### 2. Environment Variables

Create a `.env` file in the root directory and configure the following variables:

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key          # Streamlit đăng nhập
SUPABASE_SERVICE_KEY=your_supabase_service_role_key  # API lưu chat_history

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 3. Database Setup (Supabase)

This project uses Supabase to store chat history. You can use the Supabase CLI to quickly push the required table schemas to your Supabase project.

**Email confirmation redirect (required on Supabase cloud):** In [Authentication → URL Configuration](https://supabase.com/dashboard/project/_/auth/url-configuration), set:

- **Site URL:** `http://localhost:8501` (or your deployed Streamlit URL)
- **Redirect URLs:** add `http://localhost:8000/auth/confirm` (and the same with `127.0.0.1` if you use it)

Optional in `.env`:

```env
AUTH_REDIRECT_URL=http://localhost:8000/auth/confirm
STREAMLIT_URL=http://localhost:8501
```

After clicking the confirmation link in email, you should see a success page on the API (`/auth/confirm`), then sign in on the Streamlit UI.

**Where to see registered accounts:** Supabase Dashboard → **Authentication → Users** (not the `chat_history` table in Table Editor).

**Chat history permissions:** After `supabase db push`, or run the SQL in `supabase/migrations/20260515120000_grant_chat_history.sql` in the SQL Editor if history stays empty.

```bash
# Link your Supabase project (you will be prompted for your database password)
npx supabase link --project-ref <your-project-ref>

# Push the database schema to Supabase
npx supabase db push
```

### 4. Local Installation (Without Docker)

We use `uv` for lightning-fast package management.

```bash
# Install uv if you haven't already
pip install uv

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

Start the local Qdrant server using Docker:
```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_data:/qdrant/storage:z \
    qdrant/qdrant
```

Run the FastAPI backend:
```bash
uvicorn api.main:app --reload --port 8000
```

Run the Streamlit UI:
```bash
streamlit run ui/chat.py
```

### 5. Running with Docker Compose (Recommended)

To run the complete stack (Qdrant, FastAPI Backend, and Streamlit UI) via Docker Compose:

```bash
# Run backend and Qdrant only
docker compose up -d

# Run the complete stack including the Streamlit UI
docker compose --profile ui up -d --build
```
- API will be accessible at: `http://localhost:8000`
- Streamlit UI will be accessible at: `http://localhost:8501`
- Qdrant Dashboard at: `http://localhost:6333/dashboard`

## 📊 Evaluation

The project uses **Ragas** to evaluate the RAG pipeline's performance.

To run the evaluation:
```bash
# Install evaluation dependencies
uv pip install -e ".[eval]"

# Run the evaluation script
python evaluation/run_eval.py
```

## 🧪 Testing

To run unit tests using `pytest`:

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/
```

## 📝 License

This project is licensed under the MIT License.
