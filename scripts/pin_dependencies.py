import json
import os

def pin_dependencies():
    # تحديث package.json
    package_path = 'src/dashboards/package.json'
    if os.path.exists(package_path):
        with open(package_path, 'r') as f:
            data = json.load(f)
        
        for dep_type in ['dependencies', 'devDependencies']:
            if dep_type in data:
                for package, version in data[dep_type].items():
                    if '^' in version or '~' in version:
                        data[dep_type][package] = version.replace('^', '').replace('~', '')
        
        with open(package_path, 'w') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    pin_dependencies() 