# langchain_deepseek
deepseek and langchain are used together to realize RAG


## prepare
- python 3.11
- register deepseek, get api key, add DEEPSEEK_KEY = "xxx" to system variable

## run
```
uv sync

# run rag
uv run python RAG/index.py

# run rag_chat
uv run python RAG_chat/index.py
```