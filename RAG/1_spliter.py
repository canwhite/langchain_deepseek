from langchain_community.document_loaders import PyPDFLoader
# 导入文本分割器
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter


loader = PyPDFLoader("docs/第一回：Matplotlib初相识.pdf")

# 调用 PyPDFLoader Class 的函数 load对pdf文件进行加载
pages = loader.load()

# print(type(pages)) # <class 'list'>
# print(len(pages))

# page = pages[0]
# print(type(page)) #<class 'langchain_core.documents.base.Document'>
# print(page.page_content[0:500])
# print(page.metadata) #{'source': 'docs/第一回：Matplotlib初相识 .pdf', 'page': 0}


#短文本切割参数
chunk_size = 20 #设置块大小
chunk_overlap = 10 #设置块重叠大小

#长文本切割参数
large_chunk_size = 80 #设置大块大小
large_chunk_overlap = 0 #设置大块重叠大小
separators =  ["\n\n", "\n", " ", ""]


'''
参数：
separators - 分隔符字符串数组
chunk_size - 每个文档的字符数量限制
chunk_overlap - 两份文档重叠区域的长度
length_function - 长度计算函数
'''

# 初始化递归字符文本分割器
r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=separators
)
# 初始化字符文本分割器
# 字符文本分割器默认以换行符为分割符
c_splitter = CharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separator='，'
)


text = "在AI的研究中，由于大模型规模非常大，模型参数很多，在大模型上跑完来验证参数好不好训练时间成本很高，所以一般会在小模型上做消融实验来验证哪些改进是有效的再去大模型上做实验。"  #测试文本
res1 =  r_splitter.split_text(text)
print(res1)

res2 = c_splitter.split_text(text)
print(res2)


# 测试用长文本
some_text = """在编写文档时，作者将使用文档结构对内容进行分组。 \
    这可以向读者传达哪些想法是相关的。 例如，密切相关的想法\
    是在句子中。 类似的想法在段落中。 段落构成文档。 \n\n\
    段落通常用一个或两个回车符分隔。 \
    回车符是您在该字符串中看到的嵌入的“反斜杠 n”。 \
    句子末尾有一个句号，但也有一个空格。\
    并且单词之间用空格分隔"""

cl_splitter = CharacterTextSplitter(
    chunk_size=large_chunk_size,
    chunk_overlap=large_chunk_overlap,
    separator=' '
)

rl_splitter = RecursiveCharacterTextSplitter(
    chunk_size=large_chunk_size,
    chunk_overlap=large_chunk_overlap,
    separators=separators
)

res4 =  rl_splitter.split_text(some_text)
print(res4)



