# Bug: itmz_converter Y 坐标超出 iThoughts 画布范围

## 症状

126 个节点的 Markdown 生成 .itmz 文件后，iThoughts 只显示约 10 个节点，其余全部丢失。

## 根本原因

### 问题 1：Y_SCALE 值过大

- **位置**：`tools/itmz_converter.py` 第 139 行
- **原因**：Y_SCALE=80 导致 Y range 达到 -1720 to -40（span=1680），远超 iThoughts 可视范围（y ≈ -200 to 100）
- **现象**：当 sections 分布在不同 y 位置时，只有落在 viewport 内的才可见，超出范围的节点从视图中消失

### 问题 2：depth≤1 节点 Y 坐标不统一

- **原因**：原始实现中 depth=0 的根节点和 depth=1 的一级章节使用 `sibling_offset` 计算 Y 坐标，导致不同章节分布在不同 Y 位置（y=-1080, -1000, -920...）
- **现象**：即使压缩了 Y_SCALE，不同 Y 位置的节点仍会导致可视性问题

## 修复方案

### 修复 1：压缩 Y_SCALE

```python
# 修复前
sibling_offset = int((i - len(node.children) / 2) * 80)  # Y_SCALE=80 → span=1680

# 修复后
Y_SCALE = 10  # 压缩 Y 范围
sibling_offset = int((i - len(node.children) / 2) * Y_SCALE)  # span=~210
```

### 修复 2：depth≤1 节点固定在 y=0

```python
if depth <= 1:
    x = 150 if depth == 1 else 0
    y = 0  # 所有章节在同一水平线上
else:
    x = depth * x_base
    sibling_offset = int((i - len(node.children) / 2) * Y_SCALE)
    y = y_offset + sibling_offset
```

### 修复 3：子节点 Y 起始位置计算调整

```python
if child.children:
    if depth <= 1:
        child_y_start = -int((len(child.children) / 2) * Y_SCALE)
    else:
        child_y_start = y - int((len(child.children) / 2) * Y_SCALE)
```

## 验证

修复后 Y range 压缩到 -140 to 0（span=210），与 iThoughts 可视范围一致。

---

## 相关的失败测试

| 测试文件 | 结构 | 节点数 | 结果 |
|---------|------|--------|------|
| `langchain_core_v3.itmz` | Y span=1680，层级嵌套 | 126 | ❌ 只显示 10 个 |
| `langchain_core_y10.itmz` | Y span=210，层级嵌套 | 126 | ❌ 只显示 10 个（Y对齐但结构问题） |
| `langchain_core_flatY.itmz` | Y span=210，depth≤1 在 y=0 | 126 | ❌ 只显示 10 个（note 属性问题） |
| `langchain_core_noNotes.itmz` | Y span=210，无 note | 126 | ✅ 全部显示 |
| `langchain_core_sameY.itmz` | Y span=210，无 note，sameY | 49 | ✅ 全部显示 |
| `langchain_core_horizontal.itmz` | 4 sections 并排，y=-100~100 | 24 | ✅ 全部显示 |
