# langchain_deepseek
deepseek and langchain are used together to realize RAG


## prepare
- python 3.11
- pip install poetry
- register deepseek, get api key, add DEEPSEEK_KEY = "xxx" to system variable

## run
```
poetry shell
poetry install

# run rag
poetry run python RAG/index.py

# run rga_chat
poetry run python RAG_chat/index.py
```