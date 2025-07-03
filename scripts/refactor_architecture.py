import os
import shutil

def fix_architecture():
    # تقليل مستويات التداخل
    for root, dirs, files in os.walk('src'):
        if root.count(os.sep) > 3:
            new_path = root.replace(os.sep, '_', 3)
            shutil.move(root, new_path)
    
    # دمج الخدمات المتكررة
    service_dirs = [
        'src/application/services',
        'src/domain/services',
        'src/core/services',
        'src/infrastructure/services'
    ]
    merged_dir = 'src/shared/services'
    os.makedirs(merged_dir, exist_ok=True)
    
    for sdir in service_dirs:
        if os.path.exists(sdir):
            for file in os.listdir(sdir):
                shutil.move(os.path.join(sdir, file), merged_dir)
            os.rmdir(sdir)
    
    # إزالة طبقة core غير المعيارية
    if os.path.exists('src/core'):
        shutil.rmtree('src/core')

if __name__ == "__main__":
    fix_architecture() 