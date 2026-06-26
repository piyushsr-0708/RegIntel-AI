import glob, re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace literal backslashes with forward slashes inside str(PROJECT_ROOT / "...")
    def replacer(match):
        inner = match.group(1).replace('\\', '/')
        return f'str(PROJECT_ROOT / {inner})'
        
    pattern = re.compile(r'str\(PROJECT_ROOT / (.*?)\)')
    new_content, count = pattern.subn(replacer, content)
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed {filepath}: {count} replacements')

for f in glob.glob('**/*.py', recursive=True):
    if 'venv' in f or '__pycache__' in f or 'fix_paths.py' in f or 'refactor_paths.py' in f: continue
    fix_file(f)
