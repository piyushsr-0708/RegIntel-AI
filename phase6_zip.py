import zipfile
import os

def create_handover_zip():
    with zipfile.ZipFile('SuRaksha_TeamHandover.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root or 'venv' in root:
                continue
            if 'delete_candidates' in root:
                continue
            
            for f in files:
                if f.endswith('.zip') or f.endswith('.pyc'):
                    continue
                fp = os.path.join(root, f)
                zf.write(fp, os.path.relpath(fp, '.'))

def create_full_zip():
    with zipfile.ZipFile('SuRaksha_FullRepository.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root or 'venv' in root:
                continue
            for f in files:
                if f.endswith('.zip') or f.endswith('.pyc'):
                    continue
                fp = os.path.join(root, f)
                zf.write(fp, os.path.relpath(fp, '.'))

def main():
    print("Creating SuRaksha_TeamHandover.zip...")
    create_handover_zip()
    
    print("Creating SuRaksha_FullRepository.zip...")
    create_full_zip()

    # Generate ZIP_CONTENTS.md
    with zipfile.ZipFile('SuRaksha_TeamHandover.zip', 'r') as zf:
        handover_files = zf.namelist()
        
    with zipfile.ZipFile('SuRaksha_FullRepository.zip', 'r') as zf:
        full_files = zf.namelist()

    with open('docs/ZIP_CONTENTS.md', 'w', encoding='utf-8') as f:
        f.write("# ZIP Archive Contents\n\n")
        f.write("## 1. SuRaksha_TeamHandover.zip\n")
        f.write("This package is intended for the UI teammates. It contains the active codebase, docs, data, and JSON outputs, but cleanly omits deleted code and dead references.\n\n")
        f.write(f"**Total Files**: {len(handover_files)}\n\n")
        
        f.write("## 2. SuRaksha_FullRepository.zip\n")
        f.write("This is the unredacted master backup of the repository, including the `delete_candidates/`.\n\n")
        f.write(f"**Total Files**: {len(full_files)}\n")

    print("Phase 6 complete.")

if __name__ == '__main__':
    main()
