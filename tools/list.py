class List(list):
    
    def forEach(self, func):
        for index, item in enumerate(self):
            func(item, index, self)
        return self

    def map(self, func):
        return List([func(item, index, self) for index, item in enumerate(self)])

    def findIndex(self, func):
        for index, item in enumerate(self):
            if func(item, index, self):
                return index
        return -1
    
    def splice(self, start, delete_count=None, *items):
        """
        实现类似 JavaScript 中的 splice 方法。
        :param start: 开始位置
        :param delete_count: 删除的元素数量，默认为从 start 到末尾的所有元素
        :param items: 插入的元素
        :return: 删除的元素列表
        """
        if delete_count is None:
            delete_count = len(self) - start
        
        deleted_elements = self[start:start + delete_count]
        self[start:start + delete_count] = items
        
        return List(deleted_elements)

    def filter(self, func):
        """
        实现类似 JavaScript 中的 filter 方法。
        :param func: 过滤函数，返回 True 的元素将被保留
        :return: 过滤后的新列表
        """
        return List([item for index, item in enumerate(self) if func(item, index, self)])
    
    def includes(self, value):
        """
        实现类似 JavaScript 中的 includes 方法。
        :param value: 要查找的值
        :return: 如果列表中包含该值，返回 True，否则返回 False
        """
        return value in self
    
    def reduce(self, func, initial=None):
        """
        实现类似 JavaScript 中的 reduce 方法。
        :param func: 归约函数，接受累加器和当前元素
        :param initial: 初始值
        :return: 归约后的结果
        """
        it = iter(self)
        if initial is None:
            try:
                initial = next(it)
            except StopIteration:
                raise TypeError("reduce() of empty sequence with no initial value")
        accum_value = initial
        for index, item in enumerate(it):
            accum_value = func(accum_value, item, index, self)
        return accum_value

    def join(self, separator=" "):
        """
        实现类似 JavaScript 中的 join 方法。
        :param separator: 分隔符，默认为空格
        :return: 连接后的字符串
        """
        return separator.join(str(item) for item in self)

    def push(self, *items):
        """
        实现类似 JavaScript 中的 push 方法。
        :param items: 要添加到列表末尾的元素
        :return: 添加元素后的列表长度
        """
        self.extend(items)
        return len(self)

    def pop(self):
        """
        实现类似 JavaScript 中的 pop 方法。
        :return: 移除的列表末尾的元素
        """
        if not self:
            raise IndexError("pop from empty list")
        return super().pop()

    def flatMap(self, func):
        """
        实现类似 JavaScript 中的 flatMap 方法。
        :param func: 映射函数，接受当前元素并返回一个列表
        :return: 扁平化后的列表
        """
        return List([item for sublist in self for item in func(sublist)])

    

if __name__ == '__main__':


    numbers = List([1, 2, 3, 4, 5])
    # 使用 lambda 函数作为回调函数
    list = []
    numbers.forEach(lambda item, index, array: 
        #使用元祖来确保两个handle都在lambda表达式中
        (print(f"Item: {item}, Index: {index}, Array: {array}"),
         list.append(item))
    )
    print(list)


    # 调用 map 方法
    squared_numbers = numbers.map(lambda item, index, array: item ** 2)
    print(squared_numbers)


    even_index = numbers.findIndex(lambda item, index, array: item % 2 == 0)
    print(f"第一个偶数的位置是: {even_index}")


    # 使用 splice 方法
    removed_elements = numbers.splice(1, 2, 10, 20)
    print(f"删除的元素: {removed_elements}")
    print(f"修改后的列表: {numbers}")


    # 调用 filter 方法
    filtered_numbers = numbers.filter(lambda item, index, array: item % 2 == 0)
    print(f"过滤后的列表: {filtered_numbers}")


    numbers.push(100)
    print(numbers)
    numbers.pop()
    print(numbers)


    # 调用 reduce 方法
    sum_of_numbers = numbers.reduce(lambda acc, item, index, array: acc + item, 0)
    print(f"所有数字的和是: {sum_of_numbers}")