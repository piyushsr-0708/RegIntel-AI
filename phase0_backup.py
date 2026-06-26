import os
import zipfile
from datetime import datetime

def get_dir_size(path='.'):
    total = 0
    file_count = 0
    dir_count = 0
    inventory = []
    
    for root, dirs, files in os.walk(path):
        if '.git' in root or '__pycache__' in root or 'venv' in root:
            continue
        
        dir_count += len(dirs)
        for f in files:
            fp = os.path.join(root, f)
            try:
                size = os.path.getsize(fp)
                total += size
                file_count += 1
                inventory.append(f"{fp} ({size} bytes)")
            except Exception:
                pass
                
    return total, file_count, dir_count, inventory

def make_zip(zip_name, filter_func=lambda x: True):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root or 'venv' in root or 'SuRaksha_Backup' in root:
                continue
            for f in files:
                fp = os.path.join(root, f)
                if filter_func(fp) and not fp.endswith('.zip'):
                    zf.write(fp, os.path.relpath(fp, '.'))

def main():
    print("Gathering inventory...")
    total_size, file_count, dir_count, inventory = get_dir_size()
    
    with open('docs/REPOSITORY_INVENTORY_PRE.md', 'w', encoding='utf-8') as f:
        f.write("# Pre-Cleanup Repository Inventory\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n")
        f.write(f"**Total Files**: {file_count}\n")
        f.write(f"**Total Folders**: {dir_count}\n")
        f.write(f"**Total Size**: {total_size / (1024*1024):.2f} MB\n\n")
        f.write("## Files\n")
        for item in inventory:
            f.write(f"- {item}\n")
            
    print("Creating SuRaksha_Backup_PreCleanup.zip...")
    make_zip('SuRaksha_Backup_PreCleanup.zip')
    
    print("Creating SuRaksha_Backup_Docs.zip...")
    make_zip('SuRaksha_Backup_Docs.zip', lambda p: p.endswith('.md') or p.endswith('.txt'))
    
    print("Phase 0 complete.")

if __name__ == '__main__':
    main()
