---
name: markdown-to-itmz
description: Generate an iThoughts (.itmz) mind map from any Markdown file. Use when user wants to convert markdown to itmz, create a mind map from documentation, or visualize markdown structure as a思维导图.
---

# Markdown to iThoughts Mind Map Generator

## Purpose

Convert any Markdown file into an iThoughts (.itmz) mind map format.

## Input

- Source Markdown file path
- Output itmz path (optional, defaults to same location with .itmz extension)
- Optional title for the mind map root node

## Workflow

### Step 1: Locate Converter

Find `tools/itmz_converter.py` in the project:
```
tools/itmz_converter.py
```

### Step 2: Run Conversion

```bash
python3 tools/itmz_converter.py <input.md> <output.itmz>
```

Example:
```bash
python3 tools/itmz_converter.py docs/api_guide.md ~/Documents/ithoughtsx/api_guide.itmz
```

### Step 3: Default Behavior

If only input is provided, output defaults to `~/Documents/ithoughtsx/<input_stem>.itmz`:
```bash
python3 tools/itmz_converter.py docs/notes.md
# Output: ~/Documents/ithoughtsx/notes.itmz
```

### Step 4: Verify Output

Check the generated itmz:
```python
import zipfile
with zipfile.ZipFile('output.itmz', 'r') as z:
    print("Files:", z.namelist())
    xml = z.read('mapdata.xml').decode('utf-8')
    topic_count = xml.count('<topic ')
    print(f"Topics: {topic_count}")
```

## itmz Format

The converter produces:
```
itmz = zip([
    mapdata.xml,      # Mind map data (XML format)
    style.xml,        # Visual styling
    manifest.plist,   # Metadata (topic count, app info)
    preview.png       # Thumbnail placeholder
])
```

### mapdata.xml Structure

- Flat `<topic>` elements with position attributes
- UUIDs with hyphens: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Position format: `position="{x, y}"`
- Code blocks stored in `note` attribute with `&#10;` for newlines

### Position Layout Algorithm

- X coordinate: `depth * 150` (each level indented 150px)
- Y coordinate: Alternating positive/negative around parent position
- Sibling offset: `(index - sibling_count/2) * 80`

## Key Features

### Code Block Handling

```python
# Code blocks become separate nodes with note attribute
# Text shows "代码块"
# Full code stored in note attribute
```

### Markdown Parsing

- `#` to `######` → hierarchy levels 1-6
- ` ```code``` ` → code block nodes with note
- `---` → ignored (separator)
- `[text](url)` → stripped to just `text`
- `**bold**` → stripped to just `bold`
- `` `code` `` → stripped

## Output Location

Default: `~/Documents/ithoughtsx/`

Configure by providing full output path as second argument.

## Verification Checklist

- [ ] itmz file created at expected path
- [ ] ZIP contains: mapdata.xml, style.xml, manifest.plist, preview.png
- [ ] Topic count matches expected headings + code blocks
- [ ] Code examples preserved in note attributes
- [ ] Position values within reasonable bounds
- [ ] Opens correctly in iThoughts app
