from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings.openai import OpenAIEmbeddings # need open ai id
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma



embedding = HuggingFaceEmbeddings()

texts_chinese = [
    """毒鹅膏菌（Amanita phalloides）具有大型且引人注目的地上（epigeous）子实体（basidiocarp）""",
    """一种具有大型子实体的蘑菇是毒鹅膏菌（Amanita phalloides）。某些品种全白。""",
    """A. phalloides，又名死亡帽，是已知所有蘑菇中最有毒的一种。""",
]
smalldb_chinese = Chroma.from_texts(texts_chinese, embedding=embedding)
question_chinese = "告诉我关于具有大型子实体的全白色蘑菇的信息"
# sresult =  smalldb_chinese.similarity_search(question_chinese, k=2)

# MMR算法，MMR 的基本思想是同时考量查询与文档的相关度，以及文档之间的相似度。
sresult =  smalldb_chinese.max_marginal_relevance_search(question_chinese,k=2, fetch_k=3)
for doc in sresult:
    print(doc.page_content)




