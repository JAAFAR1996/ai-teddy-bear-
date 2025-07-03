import ast
import os

def split_large_files():
    for root, _, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    code = f.read()
                
                # تقسيم الملفات الكبيرة
                if len(code.splitlines()) > 300:
                    module = ast.parse(code)
                    new_dir = os.path.join(root, file.replace('.py', ''))
                    os.makedirs(new_dir, exist_ok=True)
                    
                    # تقسيم الدوال الكبيرة
                    for node in module.body:
                        if isinstance(node, ast.FunctionDef):
                            func_code = ast.unparse(node)
                            new_file = os.path.join(new_dir, f"{node.name}.py")
                            with open(new_file, 'w') as f:
                                f.write(func_code)
                    
                    os.remove(filepath)

if __name__ == "__main__":
    split_large_files() 