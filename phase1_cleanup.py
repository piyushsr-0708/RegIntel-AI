import os
import shutil
import glob

def safe_move(src, dest_dir):
    if os.path.exists(src):
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, os.path.basename(src))
        if os.path.exists(dest_path):
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            else:
                os.remove(dest_path)
        shutil.move(src, dest_dir)
        return True
    return False

def main():
    os.makedirs('archive/delete_candidates', exist_ok=True)
    os.makedirs('docs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    with open('archive_list.txt', 'r') as f: archive_files = [l.strip() for l in f if l.strip()]
    with open('delete_list.txt', 'r') as f: delete_files = [l.strip() for l in f if l.strip()]
    
    print("Moving archive files...")
    for item in archive_files:
        if item.endswith('/'): item = item[:-1]
        safe_move(item, 'archive')
        
    print("Moving delete candidates...")
    for item in delete_files:
        if item.endswith('/'): item = item[:-1]
        safe_move(item, 'archive/delete_candidates')
        
    print("Moving data directories...")
    data_dirs = ['dataset', 'requirements', 'vector_db', 'requirement_db', 'chroma_db', 'extracted_text', 'chunks']
    for d in data_dirs:
        safe_move(d, 'data')
        
    print("Moving documentation to docs/...")
    docs = glob.glob('*.md') + glob.glob('*.txt') + glob.glob('*.xlsx')
    keep_root = ['PROJECT_STATE.md', 'TEAM_HANDOVER.md', 'requirements.txt']
    
    for d in docs:
        if d not in keep_root:
            safe_move(d, 'docs')
            
    print("Phase 1 complete.")

if __name__ == '__main__':
    main()
