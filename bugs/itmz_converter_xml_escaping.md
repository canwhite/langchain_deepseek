# Bug: itmz_converter note 属性 XML 转义不完整

## 症状

修复 Y 坐标问题后，添加 note 属性（代码块内容）仍导致 iThoughts 只显示部分节点。移除 note 后正常显示全部 126 节点。

## 根本原因

- **位置**：`tools/itmz_converter.py` 第 127 行
- **原因**：`xml.sax.saxutils.escape()` 默认只转义 `&`、`<`、`>`，不转义双引号 `"`
- **触发条件**：note 内容为 Python 代码，代码中大量含双引号（如 `tool_choice="get_weather"`、`{"city": "北京"}`）
- **后果**：双引号破坏 XML 属性解析，iThoughts 解析到被破坏的 XML 后停止解析后续节点

## 失败示例

```python
# 原始 note 内容（Python 代码片段）
tool_choice="get_weather"

# 转义前（破坏 XML）
note="tool_choice="get_weather""

# 转义后（仍然错误，因为 " 没有被转义）
note="tool_choice=&quot;get_weather&quot;  ← 实际代码没有转义双引号
```

## 修复方案

### 方案 A：转义双引号（不推荐）

```python
def escape_text(text: str) -> str:
    return xml.sax.saxutils.escape(text, {'"': '&quot;'})
```

但仍存在问题：Python 代码中双引号数量多，每次转义后字符串变长，且 `&#10;` 换行符处理可能引入额外复杂性。

### 方案 B：移除 note 属性（当前采用）

不再使用 `note` 属性存储代码块，改为将代码直接嵌入 topic 的 `text` 中，用 triple backticks 包裹：

```python
if child.note:
    display_text = f"{child.text}\n```\n{child.note}\n```"
    escaped_text = escape_text(display_text)
else:
    escaped_text = escape_text(child.text)
```

**优点**：
- 不依赖 XML 属性，无需处理 note 内容的转义
- 代码块在 iThoughts 中直接可见
- text 内容天然支持多行，无需 `&#10;` 转换

**缺点**：
- 代码块 text 可能非常长
- iThoughts 中代码块节点文本过长

## 验证

| 测试文件 | note 处理方式 | 节点数 | 结果 |
|---------|-------------|--------|------|
| `langchain_core_fixed2.itmz` | note 属性，无双引号转义 | 126 | ❌ 只显示部分 |
| `langchain_core_shortNote.itmz` | note 缩短到 ~100 字符 | 126 | ❌ 只显示部分 |
| `langchain_core_noNotes.itmz` | 无 note | 126 | ✅ 全部显示 |
| `langchain_core_codeInText.itmz` | 代码嵌入 text，```包裹 | 126 | ✅ 全部显示 |
