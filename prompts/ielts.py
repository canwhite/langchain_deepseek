from tool import get_completion
from langchain.prompts import ChatPromptTemplate



'''
在市面上找到对应的模型，就可以让AI辅助自己学习。
'''


# 创建模型参数
text ="""
雅思口语考题基本上是五大类别：人，物，地点，事件，媒体。

回答的主体结构：
- topic sentence:
在讲五大类别的任何一个的时候，务必把这个原则与你联系在一起，开头的时候有个主题句，通过这句话引入下面的支持观点，
这个主题句可以通过一到两句话来完成，但最好是对你有影响的。
描述这个人---对你有影响;
描述这个物----对你有意义;
描述这个地点---对你有回忆等等...

- Supportive view:
支持观点，在这里要注意，我相信很多同学都会用观点来支持自己，但太过于白话文，
大部分用例子来支撑，部分考生喜欢用For example，First , secondly, last but not the least来讲分论点，
但这样给考官的感觉是在背作文，而不是真正的口语。
在Supportive view，
这的观点一般是需要比较正式点的语言，每讲的一句话最好不少于5个单词以下，但最好不超过5句话。
过渡词用什么好呢?
最好用well , also , actually ,as a matter of fact , you know 等等词。


-Event:
当然就是找到支持观点的例子，恰当的例子，但是字数不能过多，要简练。
"""



# 创建提示模版
prompt  = f"""
写一篇能够口述的英文文章，主题是想引入的法规，要求如下：
{text}
这篇文章要偏口语，不要用太生僻的次，能让我说两分钟左右
"""

template =  ChatPromptTemplate.from_template(prompt)

# 写入参数
messages = template.format_messages(
                    text=text)

print(get_completion(messages))


