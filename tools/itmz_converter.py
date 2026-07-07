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


def parse_markdown(filepath: str) -> MindMapNode:
    """解析 Markdown 文件，构建思维导图树结构"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    root = MindMapNode(level=0, text="")
    node_stack: list[MindMapNode] = [root]

    in_code_block = False
    code_block_lines = []

    for line in lines:
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
            continue

        if in_code_block:
            code_block_lines.append(line)
            continue

        # 分隔线忽略
        if line.strip() == '---':
            continue

        # 标题匹配
        m = re.match(r'^(#{1,6})\s+(.+)$', line.lstrip())
        if not m:
            continue

        level = len(m.group(1))
        text = m.group(2).strip()

        # 移除 Markdown 链接和粗体
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)

        add_node_to_tree(node_stack, level, text)

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
        return xml.sax.saxutils.escape(text)

    def format_timestamp() -> str:
        """生成当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    timestamp = format_timestamp()

    # 构建所有 topic 行
    lines = []

    def add_topics(node: MindMapNode, depth: int = 0, y_offset: int = 0):
        """递归添加所有子节点，使用自然树状布局"""
        x_base = 150  # 每个层级增加的固定值

        for i, child in enumerate(node.children):
            topic_id = child.node_id.upper()
            escaped_text = escape_text(child.text)

            # 计算位置
            x = depth * x_base

            # Y = 父节点Y + 兄弟节点偏移（交替正负，模拟自然树状布局）
            sibling_offset = (i - len(node.children) / 2) * 80
            y = y_offset + sibling_offset

            # 如果有 note（代码内容），转义并用 &#10; 表示换行
            note_attr = ""
            if child.note:
                escaped_note = escape_text(child.note).replace('\n', '&#10;')
                note_attr = f' note="{escaped_note}"'

            if child.children:
                # 有子节点 - 计算子节点的Y起始位置
                child_y_start = y - (len(child.children) / 2) * 80

                lines.append(
                    f'<topic uuid="{topic_id}" position="{{{x}, {y}}}" text="{escaped_text}"{note_attr} created="{timestamp}" modified="{timestamp}">'
                )
                add_topics(child, depth + 1, child_y_start)
                lines.append('</topic>')
            else:
                # 叶节点
                lines.append(
                    f'<topic uuid="{topic_id}" position="{{{x}, {y}}}" text="{escaped_text}"{note_attr} created="{timestamp}" modified="{timestamp}">'
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
