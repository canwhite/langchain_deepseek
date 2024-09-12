class Match:
    def __init__(self, value):
        self.value = value
        self.cases = []

    def with_(self, pattern, handler):
        self.cases.append((pattern, handler))
        return self

    def otherwise(self, handler):
        self.cases.append((lambda x: True, handler))
        return self

    def execute(self):
        for pattern, handler in self.cases:
            if pattern(self.value):
                return handler(self.value)
        raise ValueError("No match found")

def match(value):
    return Match(value)
 

if __name__ == '__main__':
    # 示例使用
    response = {'status': 'success'}
    # 匿名函数需要lambad关键字，add = lambda x, y: x + y
    
    '''
    #使用续行符
    result = match(response) \
        .with_(lambda x: x['status'] == 'success', lambda x: 'Success') \
        .with_(lambda x: x['status'] == 'error', lambda x: 'Error') \
        .otherwise(lambda x: 'Unknown') \
        .execute()
    '''
    #使用列表推导式，不用续行符
    result = [
        match(response)
        .with_(lambda x: x['status'] == 'success', lambda x: 'Success')
        .with_(lambda x: x['status'] == 'error', lambda x: 'Error')
        .otherwise(lambda x: 'Unknown')
        .execute()
    ][0]
    

    print(result)  # 输出: Success