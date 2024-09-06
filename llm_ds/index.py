from langchain_openai import ChatOpenAI
import os

API_KEY=  os.getenv("DEEPSEEK_KEY")
BASE_URL = "https://api.deepseek.com"


class SingletonChatOpenAI:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonChatOpenAI, cls).__new__(cls)
            cls._instance.llm = ChatOpenAI(
                model='deepseek-chat', 
                openai_api_key=API_KEY, 
                openai_api_base=BASE_URL,
                max_tokens=1024
            )
        return cls._instance

    def __getattr__(self, name):
        return getattr(self._instance.llm, name)

llm = SingletonChatOpenAI().llm




