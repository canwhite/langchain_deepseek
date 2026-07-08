#!/usr/bin/env python3
"""
itmz_converter: 将 Markdown 转换为 iThoughts 思维导图 (.itmz)

真实 itmz 格式（基于真实文件分析）:
- 文件名: mapdata.xml
- UUID 格式: 带连字符 xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- 位置格式: position="{x, y}"
- 所有 topic 扁平排列，层级由 position 决定
- 根节点 position="{0, 0}"
"""

import zipfile
import plistlib
import uuid
import re
import xml.sax.saxutils
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MindMapNode:
    """思维导图节点"""
    level: int          # 标题层级 (1-6)
    text: str           # 节点文本
    children: list['MindMapNode'] = field(default_factory=list)
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    note: str = ""      # 代码块内容存储在 note 属性中


def markdown_to_text(text: str) -> str:
    """将 Markdown 格式文本转为纯文本"""
    # 移除粗体标记 **text** → text
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    # 移除行内代码 `code` → code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 移除链接 [text](url) → text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text


def format_table(rows: list[str]) -> str:
    """将 Markdown 表格转为纯文本"""
    if not rows:
        return ""
    # 过滤掉分隔行 (|---|---|)，统计有效行
    valid_rows = []
    for row in rows:
        cells = [c.strip() for c in row.split('|')[1:-1]]
        if cells and not all(re.match(r'^[-:]+$', c) for c in cells):
            valid_rows.append(cells)
    if not valid_rows:
        return ""
    # 计算每列最大宽度
    cols = max(len(cells) for cells in valid_rows)
    widths = [0] * cols
    for cells in valid_rows:
        for j, cell in enumerate(cells):
            widths[j] = max(widths[j], len(cell))
    # 格式化每一行
    lines = []
    for cells in valid_rows:
        line = '  '.join(markdown_to_text(cells[j]).ljust(widths[j]) if j < len(cells) else ''.ljust(widths[j]) for j in range(cols))
        lines.append(line)
    return '\n'.join(lines)


def parse_markdown(filepath: str) -> MindMapNode:
    """解析 Markdown 文件，构建思维导图树结构"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    root = MindMapNode(level=0, text="")
    node_stack: list[MindMapNode] = [root]

    in_code_block = False
    code_block_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 代码块处理
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_lines = []
            else:
                in_code_block = False
                if code_block_lines:
                    # 完整代码存入 note，只在 text 中显示"代码块"
                    code_text = "代码块"
                    code_note = '\n'.join(code_block_lines)
                    code_level = node_stack[-1].level + 1 if node_stack else 1
                    node = MindMapNode(level=code_level, text=code_text, note=code_note)
                    while node_stack and node_stack[-1].level >= code_level:
                        node_stack.pop()
                    if node_stack:
                        node_stack[-1].children.append(node)
                    node_stack.append(node)
                    code_block_lines = []
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        # 分隔线忽略
        if line.strip() == '---':
            i += 1
            continue

        # 标题匹配
        m = re.match(r'^(#{1,6})\s+(.+)$', line.lstrip())
        if not m:
            i += 1
            continue

        level = len(m.group(1))
        heading_text = m.group(2).strip()

        # 移除 Markdown 链接和粗体
        heading_text = markdown_to_text(heading_text)

        # 收集标题后面的内容（列表项、段落、表格），直到下一个标题或代码块
        body_lines = []
        j = i + 1
        table_rows = []
        in_table = False

        while j < len(lines):
            next_line = lines[j].rstrip()

            # 遇到下一个标题或代码块就停止
            if next_line.strip().startswith('```') or re.match(r'^(#{1,6})\s+', next_line.lstrip()):
                break
            # 遇到分隔线也停止
            if next_line.strip() == '---':
                break

            # 表格行
            if next_line.strip().startswith('|'):
                in_table = True
                table_rows.append(next_line.strip())
                j += 1
                continue
            elif in_table and not next_line.strip():
                # 空行后结束表格
                in_table = False
                if table_rows:
                    body_lines.append(format_table(table_rows))
                    table_rows = []
                j += 1
                continue
            elif in_table:
                # 表格后非表格行，结束表格
                in_table = False
                if table_rows:
                    body_lines.append(format_table(table_rows))
                    table_rows = []

            # 列表项：- text 或 * text
            list_m = re.match(r'^[-*]\s+(.+)$', next_line.strip())
            if list_m:
                item_text = markdown_to_text(list_m.group(1).strip())
                body_lines.append(f"○ {item_text}")
            elif next_line.strip() and not next_line.startswith('#'):
                # 非空非标题行作为段落
                para = next_line.strip()
                if para:
                    para = markdown_to_text(para)
                    body_lines.append(para)

            j += 1

        # 处理末尾的表格
        if table_rows:
            body_lines.append(format_table(table_rows))

        # 合并标题和内容
        if body_lines:
            node_text = heading_text + "\n" + "\n".join(body_lines)
        else:
            node_text = heading_text

        add_node_to_tree(node_stack, level, node_text)
        i = j

    return root


def add_node_to_tree(node_stack: list[MindMapNode], level: int, text: str):
    """将节点添加到树中，维护 stack"""
    node = MindMapNode(level=level, text=text)

    while node_stack and node_stack[-1].level >= level:
        node_stack.pop()

    if node_stack:
        node_stack[-1].children.append(node)

    node_stack.append(node)


def count_topics(node: MindMapNode) -> int:
    """统计节点总数"""
    def _count(node: MindMapNode) -> int:
        count = 0
        for child in node.children:
            count += 1 + _count(child)
        return count
    return _count(node)


def generate_mapdata_xml(root: MindMapNode, title: str = "Mind Map") -> str:
    """
    生成 mapdata.xml - 正确的 iThoughts 格式

    真实格式（从真实文件分析）:
    - 所有 topic 扁平排列，不是嵌套
    - UUID 带连字符
    - position 决定位置
    """
    def escape_text(text: str) -> str:
        """转义 XML 特殊字符"""
        return xml.sax.saxutils.escape(text, {'"': '&quot;'})

    def format_timestamp() -> str:
        """生成当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    timestamp = format_timestamp()

    # 构建所有 topic 行
    lines = []

    Y_SCALE = 10  # 压缩 Y 范围，避免超出 iThoughts 画布

    def add_topics(node: MindMapNode, depth: int = 0, y_offset: int = 0):
        """递归添加所有子节点，使用自然树状布局"""
        x_base = 150  # 每个层级增加的固定值

        for i, child in enumerate(node.children):
            topic_id = child.node_id.upper()
            escaped_text = escape_text(child.text)

            # 计算位置
            # depth=0/1 的节点全部在 y=0（水平排列），避免超出画布
            if depth <= 1:
                x = 150 if depth == 1 else 0
                y = 0
            else:
                x = depth * x_base
                sibling_offset = int((i - len(node.children) / 2) * Y_SCALE)
                y = y_offset + sibling_offset

            # 如果有 note（代码块），用 ``` 包裹，换行用 &#10;
            if child.note:
                wrapped = f"```\n{child.note}\n```"
                escaped_text = escape_text(wrapped).replace('\n', '&#10;')
            else:
                escaped_text = escape_text(child.text).replace('\n', '&#10;')

            if child.children:
                # depth<=1 的节点，子节点用 Y_SCALE 布局
                if depth <= 1:
                    child_y_start = -int((len(child.children) / 2) * Y_SCALE)
                else:
                    child_y_start = y - int((len(child.children) / 2) * Y_SCALE)

                lines.append(
                    f'<topic uuid="{topic_id}" position="{{{x}, {y}}}" text="{escaped_text}" created="{timestamp}" modified="{timestamp}">'
                )
                add_topics(child, depth + 1, child_y_start)
                lines.append('</topic>')
            else:
                # 叶节点
                lines.append(
                    f'<topic uuid="{topic_id}" position="{{{x}, {y}}}" text="{escaped_text}" created="{timestamp}" modified="{timestamp}">'
                )
                lines.append('</topic>')

    # 添加根节点的直接子节点
    add_topics(root)

    topics_content = '\n'.join(lines)

    # 构建完整的 XML
    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<iThoughts version="4.0" app="com.toketaware.ithoughtsx.mas" app-version="9.4" '
        f'modified="{timestamp}" author="Python">'
        '<topics>\n'
        f'{topics_content}\n'
        '</topics><relationships>\n'
        '</relationships>\n'
        '</iThoughts>\n'
    )

    return xml_content


def generate_style_xml() -> str:
    """生成 style.xml"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<style>
  <themes>
    <theme id="default" name="Default">
      <node>
        <color>#000000</color>
        <fontname>Helvetica</fontname>
        <fontsize>14</fontsize>
        <fontstyle>0</fontstyle>
        <fgcolor>#000000</fgcolor>
        <bgcolor>#FFFFFF</bgcolor>
        <bordercolor>#888888</bordercolor>
        <borderwidth>1</borderwidth>
        <cloud>0</cloud>
      </node>
    </theme>
  </themes>
</style>
'''


def generate_manifest_plist(topic_count: int) -> bytes:
    """生成 manifest.plist"""
    manifest = {
        'app': 'com.toketaware.ithoughtsx.mas',
        'version': '9.4',
        'topicCount': topic_count,
        'preview': 'preview.png',
    }
    return plistlib.dumps(manifest)


def create_preview_png() -> bytes:
    """生成简单的预览 PNG 占位图 (1x1 透明)"""
    return bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
        0x42, 0x60, 0x82
    ])


def convert_md_to_itmz(md_path: str, output_path: str, title: str = None) -> None:
    """将 Markdown 文件转换为 iThoughts 思维导图"""
    md_path = Path(md_path)

    if title is None:
        title = md_path.stem

    # 解析 Markdown
    root = parse_markdown(str(md_path))

    # 统计节点数
    topic_count = count_topics(root)

    # 生成 XML 文件
    mapdata_xml = generate_mapdata_xml(root, title)
    style_xml = generate_style_xml()
    manifest_plist = generate_manifest_plist(topic_count)
    preview_png = create_preview_png()

    # 确保输出目录存在
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 打包为 itmz
    try:
        with zipfile.ZipFile(
            output_path,
            'w',
            compression=zipfile.ZIP_STORED
        ) as zf:
            zf.writestr('mapdata.xml', mapdata_xml.encode('utf-8'))
            zf.writestr('style.xml', style_xml.encode('utf-8'))
            zf.writestr('manifest.plist', manifest_plist)
            zf.writestr('preview.png', preview_png)
    except PermissionError as e:
        raise RuntimeError(
            f"无法写入文件 {output_path}，请关闭 iThoughts 中打开的文件"
        ) from e

    print(f"转换完成: {output_path}")
    print(f"节点数: {topic_count}")


def main():
    import sys

    md_file = sys.argv[1] if len(sys.argv) > 1 else 'docs/langchain_core.md'
    output_file = sys.argv[2] if len(sys.argv) > 2 else '~/Documents/ithoughtsx/langchain_core.itmz'

    output_file = Path(output_file).expanduser()

    md_path = Path(md_file)
    if md_path.stat().st_size > 50 * 1024 * 1024:
        print("错误: Markdown 文件超过 50MB 限制")
        sys.exit(1)

    convert_md_to_itmz(str(md_path), str(output_file))


if __name__ == '__main__':
    main()
