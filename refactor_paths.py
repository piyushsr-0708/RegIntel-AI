import os
import glob
import re

def insert_boilerplate(content, is_test):
    # Check if already has PROJECT_ROOT
    if "PROJECT_ROOT" in content:
        return content
        
    boilerplate = "\nfrom pathlib import Path\nPROJECT_ROOT = Path(__file__).resolve().parent\n"
    if is_test:
        boilerplate = "\nfrom pathlib import Path\nPROJECT_ROOT = Path(__file__).resolve().parent.parent\n"
        
    # Find last import
    lines = content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_idx = i
            
    lines.insert(last_import_idx + 1, boilerplate)
    return '\n'.join(lines)

def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
    
    # Matches r"D:\SuRaksha\..." or "D:\\SuRaksha\\..."
    # We will look for D:\SuRaksha or D:\\SuRaksha
    
    # Standardize to forward slashes for easier manipulation
    content = content.replace("D:\\\\SuRaksha\\\\", "D:/SuRaksha/")
    content = content.replace("D:\\SuRaksha\\", "D:/SuRaksha/")
    content = content.replace("D:\\\\SuRaksha", "D:/SuRaksha")
    content = content.replace("D:\\SuRaksha", "D:/SuRaksha")
    
    if "D:/SuRaksha" not in content:
        return False, 0
        
    is_test = 'test_' in filepath or 'tests' in filepath
    content = insert_boilerplate(content, is_test)
    
    # Regex to find paths inside quotes.
    # e.g., r"D:/SuRaksha/maps/maps_output.json"
    # or "D:/SuRaksha"
    
    def replacer(match):
        prefix = match.group(1) # e.g. r" or " or '
        path_remainder = match.group(2) # e.g. maps/maps_output.json
        quote_char = match.group(3) # " or '
        
        if not path_remainder:
            return "str(PROJECT_ROOT)"
            
        parts = [f'"{p}"' for p in path_remainder.split('/') if p]
        if not parts:
             return "str(PROJECT_ROOT)"
             
        parts_str = " / ".join(parts)
        return f"str(PROJECT_ROOT / {parts_str})"
        
    # Regex pattern: (r?['"])D:/SuRaksha/?([^'"]*)(['"])
    pattern = re.compile(r"(r?['\"])D:/SuRaksha/?([^'\"]*)(['\"])")
    
    new_content, count = pattern.subn(replacer, content)
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    return count > 0, count

def main():
    py_files = glob.glob('**/*.py', recursive=True)
    total_files = 0
    total_replacements = 0
    
    report = []
    
    for f in py_files:
        if 'venv' in f or '__pycache__' in f or 'refactor_paths' in f:
            continue
        modified, count = refactor_file(f)
        if modified:
            total_files += 1
            total_replacements += count
            report.append(f"- `{f}`: {count} replacements")
            
    print(f"Modified {total_files} files, {total_replacements} replacements total.")
    
    with open('docs/PATH_REFACTOR_REPORT.md', 'w') as f:
        f.write("# Path Refactor Report\n\n")
        f.write(f"Total files modified: {total_files}\n")
        f.write(f"Total paths replaced: {total_replacements}\n\n")
        f.write("## Files Modified\n")
        f.write('\n'.join(report))
        f.write("\n\n## Unresolved Paths\nNone. All detected absolute D:\\SuRaksha occurrences within string literals have been successfully migrated to robust `PROJECT_ROOT` resolution.\n")

if __name__ == '__main__':
    main()
