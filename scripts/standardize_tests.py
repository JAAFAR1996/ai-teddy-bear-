import os
import subprocess

def standardize_tests():
    # تحويل اختبارات Playwright إلى Python
    playwright_dir = 'tests/e2e'
    if os.path.exists(playwright_dir):
        for file in os.listdir(playwright_dir):
            if file.endswith('.js'):
                js_file = os.path.join(playwright_dir, file)
                py_file = js_file.replace('.js', '.py')
                
                # تحويل باستخدام ChatGPT API
                subprocess.run([
                    'curl', '-X', 'POST', 
                    'https://api.openai.com/v1/engines/davinci-codex/completions',
                    '-H', 'Authorization: Bearer YOUR_API_KEY',
                    '-d', f'{{"prompt": "Convert this JavaScript to Python:\\n{open(js_file).read()}", "max_tokens": 500}}',
                    '-o', py_file
                ])
                
                os.remove(js_file)

if __name__ == "__main__":
    standardize_tests() 