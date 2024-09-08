# langchain_deepseek
deepseek and langchain are used together to realize RAG


## prepare
- python 3.11
- pip install poetry
- 注册deepseek，拿到api key，在系统变量里添加 DEEPSEEK_KEY = "xxx"

## run
```
poetry shell
poetry install
poetry run python RAG/index.py
```