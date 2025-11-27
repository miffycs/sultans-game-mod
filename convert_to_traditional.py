#!/usr/bin/env python3
"""
Convert Simplified Chinese to Traditional Chinese in all JSON files
Handles JSON with comments and preserves formatting
"""
import re
from pathlib import Path
from opencc import OpenCC

# Initialize converter (Simplified to Traditional)
cc = OpenCC('s2t')  # s2t = Simplified to Traditional

# Manual corrections that should always be applied
MANUAL_CORRECTIONS = {
    '裏': '裡',
    '牀': '床',
    '纔': '才',
    '爲': '為',
    '羣': '群',
    '衆': '眾',
    # '羣衆': '群眾',
    # '羣龍無首': '群龍無首',
    '喫': '吃',
    '瞭': '了',
    '黴': '霉',
}

def apply_manual_corrections(text):
    """Apply manual corrections for specific cases"""
    for wrong, correct in MANUAL_CORRECTIONS.items():
        text = text.replace(wrong, correct)
    return text

def convert_chinese_in_text(text):
    """
    Convert ALL Chinese text including in strings, comments, and anywhere else.
    Preserves JSON structure and formatting.
    """
    result = []
    i = 0
    in_string = False
    escape_next = False
    current_segment = []  # Can be string content or non-string content
    string_start_char = None

    while i < len(text):
        char = text[i]

        # Handle escape sequences
        if escape_next:
            current_segment.append(char)
            escape_next = False
            i += 1
            continue

        if char == '\\':
            current_segment.append(char)
            escape_next = True
            i += 1
            continue

        # Handle string boundaries
        if char in ('"', "'"):
            if not in_string:
                # Convert and flush any accumulated non-string content
                if current_segment:
                    segment_text = ''.join(current_segment)
                    converted_segment = cc.convert(segment_text)
                    result.append(converted_segment)
                    current_segment = []

                # Starting a string
                in_string = True
                string_start_char = char
                result.append(char)
            elif char == string_start_char:
                # Ending a string - convert accumulated content
                string_content = ''.join(current_segment)
                converted_content = cc.convert(string_content)
                result.append(converted_content)
                result.append(char)
                current_segment = []
                in_string = False
                string_start_char = None
            else:
                # Different quote type within string
                current_segment.append(char)
            i += 1
            continue

        # Accumulate content (both in strings and outside)
        current_segment.append(char)
        i += 1

    # Convert and flush any remaining content
    if current_segment:
        segment_text = ''.join(current_segment)
        converted_segment = cc.convert(segment_text)
        result.append(converted_segment)

    converted_text = ''.join(result)

    # Apply manual corrections
    converted_text = apply_manual_corrections(converted_text)

    # Remove trailing spaces from each line
    lines = converted_text.split('\n')
    lines = [line.rstrip() for line in lines]
    converted_text = '\n'.join(lines)

    return converted_text

def convert_json_file(file_path):
    """Convert a single JSON file"""
    try:
        print(f"Converting: {file_path}")

        # Read the file content as text
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convert Chinese text while preserving structure
        converted_content = convert_chinese_in_text(content)

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(converted_content)

        return True
    except Exception as e:
        print(f"Error converting {file_path}: {str(e)[:100]}")
        return False

def main():
    """Convert all JSON files in the workspace"""
    workspace_root = Path(__file__).parent

    # Find all JSON files
    json_files = []
    json_files.extend(workspace_root.glob('*.json'))
    json_files.extend(workspace_root.glob('config/**/*.json'))

    print(f"Found {len(json_files)} JSON files to convert\n")

    success_count = 0
    failed_files = []

    for json_file in json_files:
        if convert_json_file(json_file):
            success_count += 1
        else:
            failed_files.append(json_file.name)

    print(f"\n✓ Successfully converted {success_count}/{len(json_files)} files")

    if failed_files:
        print(f"\n⚠ Failed files ({len(failed_files)}):")
        for filename in failed_files[:10]:  # Show first 10
            print(f"  - {filename}")
        if len(failed_files) > 10:
            print(f"  ... and {len(failed_files) - 10} more")

if __name__ == '__main__':
    main()
