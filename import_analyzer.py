import ast
import os
import glob

def analyze_imports():
    py_files = glob.glob("*.py")
    local_modules = [f[:-3] for f in py_files]
    
    dependencies = {}
    for f in py_files:
        with open(f, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read(), filename=f)
            except Exception:
                continue
            
            deps = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        deps.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        deps.add(node.module.split('.')[0])
            
            # Filter to only local modules
            local_deps = [d for d in deps if d in local_modules]
            dependencies[f] = local_deps
            
    print("DEPENDENCY MAP:")
    for f, deps in dependencies.items():
        print(f"{f}: {deps}")

if __name__ == "__main__":
    analyze_imports()
