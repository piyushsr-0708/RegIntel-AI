import glob

def fix_paths():
    for f in glob.glob('**/*.py', recursive=True):
        if 'venv' in f or '__pycache__' in f or f.startswith('archive'): continue
        
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        original = content
        
        # Replace occurrences like PROJECT_ROOT / "data/requirements/
        replacements = {
            'PROJECT_ROOT / "data/requirements/': 'PROJECT_ROOT / "data/requirements/',
            "PROJECT_ROOT / 'data/requirements/": "PROJECT_ROOT / 'data/requirements/",
            'PROJECT_ROOT / "data/dataset/': 'PROJECT_ROOT / "data/dataset/',
            "PROJECT_ROOT / 'data/dataset/": "PROJECT_ROOT / 'data/dataset/",
            'PROJECT_ROOT / "data/vector_db/': 'PROJECT_ROOT / "data/vector_db/',
            "PROJECT_ROOT / 'data/vector_db/": "PROJECT_ROOT / 'data/vector_db/",
            'PROJECT_ROOT / "data/chroma_db/': 'PROJECT_ROOT / "data/chroma_db/',
            "PROJECT_ROOT / 'data/chroma_db/": "PROJECT_ROOT / 'data/chroma_db/",
            'PROJECT_ROOT / "data/requirement_db/': 'PROJECT_ROOT / "data/requirement_db/',
            "PROJECT_ROOT / 'data/requirement_db/": "PROJECT_ROOT / 'data/requirement_db/",
            'PROJECT_ROOT / "data/extracted_text/': 'PROJECT_ROOT / "data/extracted_text/',
            "PROJECT_ROOT / 'data/extracted_text/": "PROJECT_ROOT / 'data/extracted_text/",
            'PROJECT_ROOT / "data/chunks/': 'PROJECT_ROOT / "data/chunks/',
            "PROJECT_ROOT / 'data/chunks/": "PROJECT_ROOT / 'data/chunks/"
        }
        
        for k, v in replacements.items():
            content = content.replace(k, v)
            
        if content != original:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Updated paths in {f}")

if __name__ == '__main__':
    fix_paths()
