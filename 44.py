#!/usr/bin/env python3
import json
import math

def split_sarif_into_chunks(input_file, num_chunks=5):
    """تقسيم ملف SARIF إلى عدة أجزاء متساوية"""
    
    print(f"🔄 تقسيم {input_file} إلى {num_chunks} أجزاء...")
    
    try:
        # قراءة الملف الأصلي
        with open(input_file, 'r', encoding='utf-8') as f:
            sarif_data = json.load(f)
        
        # استخراج المشاكل
        issues = sarif_data['runs'][0]['results']
        total_issues = len(issues)
        
        print(f"📊 إجمالي المشاكل: {total_issues}")
        
        # حساب حجم كل جزء
        chunk_size = math.ceil(total_issues / num_chunks)
        print(f"📦 حجم كل جزء: ~{chunk_size} مشكلة")
        
        created_files = []
        
        # تقسيم وإنشاء الملفات
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_issues)
            
            # التأكد من وجود مشاكل في هذا الجزء
            if start_idx >= total_issues:
                break
            
            # استخراج مشاكل هذا الجزء
            chunk_issues = issues[start_idx:end_idx]
            
            # إنشاء نسخة من البيانات الأصلية
            chunk_sarif = json.loads(json.dumps(sarif_data))
            chunk_sarif['runs'][0]['results'] = chunk_issues
            
            # إضافة معلومات الجزء
            if 'properties' not in chunk_sarif:
                chunk_sarif['properties'] = {}
            
            chunk_sarif['properties']['chunkNumber'] = i + 1
            chunk_sarif['properties']['totalChunks'] = num_chunks
            chunk_sarif['properties']['chunkSize'] = len(chunk_issues)
            chunk_sarif['properties']['startIndex'] = start_idx
            chunk_sarif['properties']['endIndex'] = end_idx - 1
            
            # تحديد اسم الملف
            base_name = input_file.replace('.json', '')
            chunk_filename = f"{base_name}_part_{i+1}_of_{num_chunks}.json"
            
            # حفظ الجزء
            with open(chunk_filename, 'w', encoding='utf-8') as f:
                json.dump(chunk_sarif, f, indent=2, ensure_ascii=False)
            
            created_files.append((chunk_filename, len(chunk_issues)))
            print(f"✅ الجزء {i+1}: {len(chunk_issues)} مشكلة → {chunk_filename}")
        
        # ملخص النتائج
        print(f"\n🎉 تم تقسيم {total_issues} مشكلة إلى {len(created_files)} ملف:")
        total_chunks = 0
        for filename, count in created_files:
            total_chunks += count
            print(f"   📁 {filename}: {count} مشكلة")
        
        print(f"\n✅ التحقق: {total_chunks} مشكلة (المجموع الأصلي: {total_issues})")
        
        # إنشاء بروموتات جاهزة
        create_agent_prompts(created_files, base_name)
        
        return created_files
        
    except FileNotFoundError:
        print(f"❌ خطأ: لم يتم العثور على الملف {input_file}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ خطأ في تحليل JSON: {e}")
        return []
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return []

def create_agent_prompts(created_files, base_name):
    """إنشاء بروموتات جاهزة للـ agents"""
    
    priority_level = "MEDIUM"
    if "critical" in base_name.lower():
        priority_level = "CRITICAL"
    elif "high" in base_name.lower():
        priority_level = "HIGH"
    elif "low" in base_name.lower():
        priority_level = "LOW"
    elif "trivial" in base_name.lower():
        priority_level = "TRIVIAL"
    
    prompts_content = f"""# 🤖 بروموتات الـ AI Agents للملفات المقسمة

## ملفات {priority_level} Priority المقسمة:

"""
    
    agent_names = ["Alpha", "Beta", "Gamma", "Delta", "Echo"]
    
    for i, (filename, count) in enumerate(created_files):
        agent_name = agent_names[i] if i < len(agent_names) else f"Agent_{i+1}"
        
        prompts_content += f"""
### 🤖 Agent {agent_name}

**الملف المخصص**: `{filename}`
**عدد المشاكل**: {count}

**البروموت**:
```
You are Agent {agent_name} - {priority_level} Priority Specialist.

MISSION: Read file: {filename}
Fix ALL {count} {priority_level.lower()}-priority issues systematically.

FOCUS AREAS:
- Apply appropriate refactoring patterns for {priority_level.lower()} issues
- Work through issues methodically
- Preserve all existing functionality
- Use clean, maintainable coding practices

PROGRESS REPORTING:
Report every {10 if count < 50 else 20} fixes in format:
"Agent {agent_name} Progress: X/{count} completed - [brief description]"

QUALITY STANDARDS:
- Reduce complexity where applicable
- Extract reusable components
- Maintain code readability
- Follow best practices

Start immediately with {filename} and work through ALL {count} issues.
```

---
"""
    
    # حفظ البروموتات
    prompts_filename = f"{base_name}_agent_prompts.md"
    with open(prompts_filename, 'w', encoding='utf-8') as f:
        f.write(prompts_content)
    
    print(f"📋 تم إنشاء بروموتات الـ Agents: {prompts_filename}")

def main():
    """الدالة الرئيسية"""
    import sys
    
    if len(sys.argv) < 2:
        print("الاستخدام:")
        print("  python script.py sarif_medium_priority.json")
        print("  python script.py sarif_medium_priority.json 5")
        sys.exit(1)
    
    input_file = sys.argv[1]
    num_chunks = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(f"🚀 بدء تقسيم الملف: {input_file}")
    
    created_files = split_sarif_into_chunks(input_file, num_chunks)
    
    if created_files:
        print(f"\n✅ تم الانتهاء! يمكنك الآن توزيع الملفات على {len(created_files)} agents")
        print("\nالملفات المُنشأة:")
        for filename, count in created_files:
            print(f"  📁 {filename}")
    else:
        print("❌ فشل في تقسيم الملف")

if __name__ == "__main__":
    main()