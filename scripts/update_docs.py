import os
import subprocess

def update_docs():
    # تحديث وثائق العمارة
    with open('ARCHITECTURE.md', 'a') as f:
        f.write("\n\n## التحديثات الجديدة\n")
        f.write("- تم توحيد هيكل الخدمات\n")
        f.write("- تم تقليل مستويات التداخل\n")
    
    # إنشاء وثائق OpenAPI
    subprocess.run([
        'python', '-m', 'swagger_doc_generator',
        '--input', 'api/endpoints',
        '--output', 'docs/openapi.yaml'
    ])

if __name__ == "__main__":
    update_docs() 