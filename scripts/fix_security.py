import os
import subprocess

def fix_security():
    # تحليل ملفات PDF لمشاكل moderation_service
    problem_dir = "ملف مشاكل moderation_service.py"
    if os.path.exists(problem_dir):
        for pdf_file in os.listdir(problem_dir):
            if pdf_file.endswith('.pdf'):
                # تحويل PDF إلى نص وتحليل المشاكل
                text = subprocess.check_output(['pdftotext', os.path.join(problem_dir, pdf_file), '-'])
                issues = text.split('Critical Issue:')
                
                # تطبيق الإصلاحات
                for issue in issues:
                    if 'SQL Injection' in issue:
                        # إصلاح ثغرات SQL Injection
                        subprocess.run([
                            'sed', '-i', 
                            's/execute(f"SELECT/execute("SELECT/',
                            'src/infrastructure/security/database.py'
                        ])
    
    # تدقيق شامل للأمان
    subprocess.run(['bandit', '-r', 'src/infrastructure/security/'])

if __name__ == "__main__":
    fix_security() 