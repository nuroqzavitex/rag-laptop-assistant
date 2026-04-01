import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from types import SimpleNamespace

load_dotenv()

_ROOT = Path(__file__).parent


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_config() -> SimpleNamespace:
    s = _load_yaml(_ROOT / "settings.yaml")

    c = SimpleNamespace()

    # API keys — ưu tiên .env, fallback sang settings.yaml
    c.GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY",  s["api"]["gemini_key"])
    c.OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY",  s["api"]["openai_key"])

    # Paths
    c.DATA_FILES      = s["paths"]["data_files"]
    c.CHROMA_DB_PATH  = s["paths"]["chroma_db"]
    c.COLLECTION_NAME = s["paths"]["collection_name"]

    # Embedding
    c.EMBEDDING_MODEL      = s["embedding"]["model"]
    c.EMBEDDING_BATCH_SIZE = s["embedding"]["batch_size"]

    # LLM
    c.LLM_MODEL       = s["llm"]["model"]
    c.LLM_TEMPERATURE = s["llm"]["temperature"]
    c.LLM_MAX_TOKENS  = s["llm"]["max_tokens"]

    # Retrieval
    c.TOP_K_VECTOR   = s["retrieval"]["top_k_vector"]
    c.TOP_K_FINAL    = s["retrieval"]["top_k_final"]
    c.VECTOR_WEIGHT  = s["retrieval"]["vector_weight"]
    c.BM25_WEIGHT    = s["retrieval"]["bm25_weight"]

    # Prompt
    c.SYSTEM_PROMPT = s["system_prompt"]

    return c


cfg = _build_config()


