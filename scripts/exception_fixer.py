#!/usr/bin/env python3
"""
🛡️ Exception Handler Fixer - AI Teddy Bear Project
إصلاح تلقائي لمشاكل Exception Handling في الكود

Lead Architect: جعفر أديب (Jaafar Adeeb)
"""

import re
import os
import ast
from pathlib import Path
from typing import List, Tuple, Dict
import shutil

class ExceptionHandlerFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixed_files = 0
        self.total_fixes = 0
        
        # أنماط Exception Handling السيئة
        self.bad_patterns = {
            # except: بدون تحديد نوع
            r'except\s*:\s*$': self._fix_bare_except,
            r'except\s*:\s*\n': self._fix_bare_except,
            
            # except Exception: واسع جداً
            r'except\s+Exception\s*:\s*$': self._fix_broad_exception,
            r'except\s+Exception\s*:\s*\n': self._fix_broad_exception,
            
            # except: pass - تجاهل صامت
            r'except\s*:\s*pass': self._fix_silent_except,
            r'except\s+Exception\s*:\s*pass': self._fix_silent_exception,
            
            # print في except blocks
            r'except.*:\s*\n\s*print\(': self._fix_print_in_except,
        }
        
        # استثناءات محددة حسب السياق
        self.context_exceptions = {
            'file': ['FileNotFoundError', 'PermissionError', 'IOError'],
            'network': ['ConnectionError', 'TimeoutError', 'requests.RequestException'],
            'database': ['sqlite3.Error', 'SQLAlchemyError', 'psycopg2.Error'],
            'validation': ['ValueError', 'TypeError', 'ValidationError'],
            'parsing': ['json.JSONDecodeError', 'yaml.YAMLError', 'ParseError'],
            'import': ['ImportError', 'ModuleNotFoundError'],
            'key': ['KeyError', 'AttributeError'],
            'index': ['IndexError', 'KeyError']
        }
    
    def _detect_context(self, code_block: str) -> str:
        """تحديد سياق الكود لاختيار الاستثناء المناسب"""
        code_lower = code_block.lower()
        
        # فحص وجود كلمات مفتاحية
        if any(keyword in code_lower for keyword in ['open(', 'file', 'read', 'write']):
            return 'file'
        elif any(keyword in code_lower for keyword in ['request', 'http', 'url', 'connection']):
            return 'network'
        elif any(keyword in code_lower for keyword in ['database', 'db', 'sql', 'query']):
            return 'database'
        elif any(keyword in code_lower for keyword in ['json', 'yaml', 'parse', 'decode']):
            return 'parsing'
        elif any(keyword in code_lower for keyword in ['import', 'module']):
            return 'import'
        elif any(keyword in code_lower for keyword in ['[', ']', 'index', 'get(']):
            return 'index'
        elif any(keyword in code_lower for keyword in ['int(', 'float(', 'str(']):
            return 'validation'
        else:
            return 'general'
    
    def _fix_bare_except(self, match, context: str, file_content: str) -> str:
        """إصلاح except: بدون تحديد نوع"""
        context_type = self._detect_context(context)
        exceptions = self.context_exceptions.get(context_type, ['Exception'])
        
        if len(exceptions) == 1:
            exception_type = exceptions[0]
        else:
            exception_type = exceptions[0]  # استخدام الأول كافتراضي
        
        return f'''except {exception_type} as e:
    logger.error(f"Error in operation: {{e}}", exc_info=True)'''
    
    def _fix_broad_exception(self, match, context: str, file_content: str) -> str:
        """إصلاح except Exception: واسع جداً"""
        context_type = self._detect_context(context)
        exceptions = self.context_exceptions.get(context_type, ['Exception'])
        
        if context_type != 'general' and len(exceptions) > 1:
            # استخدام استثناءات متعددة محددة
            exception_block = ""
            for i, exc in enumerate(exceptions[:2]):  # أول استثناءين
                if i == 0:
                    exception_block += f'''except {exc} as e:
    logger.warning(f"{exc.__name__}: {{e}}")'''
                else:
                    exception_block += f'''
except {exc} as e:
    logger.error(f"{exc.__name__}: {{e}}")'''
            
            exception_block += '''
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)'''
            
            return exception_block
        else:
            return '''except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)'''
    
    def _fix_silent_except(self, match, context: str, file_content: str) -> str:
        """إصلاح except: pass التجاهل الصامت"""
        context_type = self._detect_context(context)
        exceptions = self.context_exceptions.get(context_type, ['Exception'])
        exception_type = exceptions[0]
        
        return f'''except {exception_type} as e:
    logger.warning(f"Ignoring error: {{e}}")'''
    
    def _fix_silent_exception(self, match, context: str, file_content: str) -> str:
        """إصلاح except Exception: pass"""
        return '''except Exception as e:
    logger.warning(f"Ignored exception: {e}")'''
    
    def _fix_print_in_except(self, match, context: str, file_content: str) -> str:
        """إصلاح print statements في except blocks"""
        # استخراج النص المطبوع
        print_match = re.search(r'print\((.*?)\)', match.group(0))
        if print_match:
            print_content = print_match.group(1)
            return f'''except Exception as e:
    logger.error(f"Error: {{e}} - Original: {print_content}")'''
        else:
            return '''except Exception as e:
    logger.error(f"Error: {e}")'''
    
    def _add_logging_import(self, file_content: str) -> str:
        """إضافة استيراد logging إذا لم يكن موجوداً"""
        if 'import logging' not in file_content and 'structlog' not in file_content:
            # إضافة في بداية الملف بعد docstring
            lines = file_content.split('\n')
            insert_index = 0
            
            # تخطي docstring في بداية الملف
            in_docstring = False
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if not in_docstring:
                        in_docstring = True
                    elif stripped.endswith('"""') or stripped.endswith("'''"):
                        in_docstring = False
                        insert_index = i + 1
                        break
                elif not in_docstring and stripped and not stripped.startswith('#'):
                    insert_index = i
                    break
            
            # إضافة استيراد logging
            lines.insert(insert_index, 'import structlog')
            lines.insert(insert_index + 1, 'logger = structlog.get_logger(__name__)')
            lines.insert(insert_index + 2, '')
            
            return '\n'.join(lines)
        
        return file_content
    
    def analyze_file(self, file_path: Path) -> Dict:
        """تحليل ملف Python للعثور على مشاكل Exception Handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # فحص الأنماط السيئة
            for pattern, fixer_func in self.bad_patterns.items():
                matches = list(re.finditer(pattern, content, re.MULTILINE))
                for match in matches:
                    # الحصول على السياق (الأسطر المحيطة)
                    lines = content.split('\n')
                    line_num = content[:match.start()].count('\n')
                    
                    context_start = max(0, line_num - 3)
                    context_end = min(len(lines), line_num + 3)
                    context = '\n'.join(lines[context_start:context_end])
                    
                    issues.append({
                        'pattern': pattern,
                        'match': match,
                        'line_num': line_num + 1,
                        'context': context,
                        'fixer': fixer_func
                    })
            
            return {
                'file_path': file_path,
                'content': content,
                'issues': issues,
                'needs_logging': 'import logging' not in content and 'structlog' not in content
            }
            
        except Exception as e:
            print(f"❌ خطأ في تحليل {file_path}: {e}")
            return None
    
    def fix_file(self, analysis: Dict) -> bool:
        """إصلاح ملف واحد"""
        if not analysis or not analysis['issues']:
            return False
        
        file_path = analysis['file_path']
        content = analysis['content']
        
        print(f"🔧 إصلاح {file_path}...")
        print(f"   🔍 وُجد {len(analysis['issues'])} مشكلة")
        
        # إنشاء نسخة احتياطية
        backup_path = file_path.with_suffix('.py.backup')
        shutil.copy2(file_path, backup_path)
        
        # تطبيق الإصلاحات
        fixes_applied = 0
        for issue in reversed(analysis['issues']):  # من الأسفل للأعلى لتجنب تغيير المواضع
            try:
                match = issue['match']
                context = issue['context']
                fixer_func = issue['fixer']
                
                # تطبيق الإصلاح
                replacement = fixer_func(match, context, content)
                content = content[:match.start()] + replacement + content[match.end():]
                fixes_applied += 1
                
                print(f"   ✅ أُصلح: السطر {issue['line_num']}")
                
            except Exception as e:
                print(f"   ❌ فشل إصلاح السطر {issue['line_num']}: {e}")
        
        # إضافة استيراد logging إذا لزم الأمر
        if analysis['needs_logging']:
            content = self._add_logging_import(content)
            print(f"   📦 أُضيف استيراد structlog")
        
        # حفظ الملف المُصلح
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ تم حفظ {file_path} مع {fixes_applied} إصلاح")
            self.total_fixes += fixes_applied
            return True
            
        except Exception as e:
            print(f"   ❌ خطأ في حفظ {file_path}: {e}")
            # استعادة من النسخة الاحتياطية
            shutil.copy2(backup_path, file_path)
            return False
    
    def fix_project_exceptions(self, target_dirs: List[str] = None) -> Dict:
        """إصلاح Exception Handling في المشروع كاملاً"""
        if target_dirs is None:
            target_dirs = ['src']
        
        print("🛡️ بدء إصلاح Exception Handling...")
        print("=" * 50)
        
        results = {
            'files_analyzed': 0,
            'files_fixed': 0,
            'total_issues': 0,
            'total_fixes': 0,
            'failed_files': []
        }
        
        for target_dir in target_dirs:
            target_path = Path(target_dir)
            if not target_path.exists():
                print(f"⚠️ تخطي {target_dir} - المجلد غير موجود")
                continue
            
            # العثور على جميع ملفات Python
            python_files = list(target_path.rglob("*.py"))
            
            for py_file in python_files:
                # تخطي ملفات الاختبار والتكوين
                if any(skip in str(py_file) for skip in ['test_', '__pycache__', '.backup']):
                    continue
                
                results['files_analyzed'] += 1
                
                # تحليل الملف
                analysis = self.analyze_file(py_file)
                if not analysis:
                    continue
                
                results['total_issues'] += len(analysis['issues'])
                
                # إصلاح الملف إذا كان يحتوي على مشاكل
                if analysis['issues']:
                    if self.fix_file(analysis):
                        results['files_fixed'] += 1
                        self.fixed_files += 1
                    else:
                        results['failed_files'].append(str(py_file))
        
        results['total_fixes'] = self.total_fixes
        
        # تقرير النتائج
        print("\n" + "=" * 50)
        print("📊 نتائج إصلاح Exception Handling:")
        print(f"📁 ملفات فُحصت: {results['files_analyzed']}")
        print(f"🔧 ملفات أُصلحت: {results['files_fixed']}")
        print(f"🔍 مشاكل وُجدت: {results['total_issues']}")
        print(f"✅ إصلاحات طُبقت: {results['total_fixes']}")
        
        if results['failed_files']:
            print(f"❌ ملفات فشلت: {len(results['failed_files'])}")
            for failed_file in results['failed_files']:
                print(f"   - {failed_file}")
        
        return results
    
    def create_exception_guidelines(self):
        """إنشاء دليل Exception Handling للمطورين"""
        guidelines = """# 🛡️ Exception Handling Guidelines - AI Teddy Bear Project

## ✅ Best Practices

### 1. Use Specific Exceptions
```python
# ❌ Bad
try:
    data = json.loads(response)
except:
    pass

# ✅ Good
try:
    data = json.loads(response)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON response: {e}")
    raise DataProcessingError(f"Failed to parse response: {e}")
```

### 2. Always Log Errors
```python
# ❌ Bad
try:
    process_data()
except Exception:
    pass

# ✅ Good
try:
    process_data()
except ValidationError as e:
    logger.warning(f"Data validation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error in data processing: {e}", exc_info=True)
    raise ProcessingError(f"Data processing failed: {e}")
```

### 3. Context-Specific Exception Handling
```python
# File operations
try:
    with open(file_path, 'r') as f:
        content = f.read()
except FileNotFoundError as e:
    logger.error(f"File not found: {file_path}")
    raise FileProcessingError(f"Required file missing: {file_path}")
except PermissionError as e:
    logger.error(f"Permission denied: {file_path}")
    raise FileProcessingError(f"Cannot access file: {file_path}")
except IOError as e:
    logger.error(f"IO error reading file: {e}")
    raise FileProcessingError(f"Failed to read file: {e}")
```

## 📋 Exception Categories by Context

### File Operations
- `FileNotFoundError`
- `PermissionError` 
- `IOError`

### Network Operations
- `ConnectionError`
- `TimeoutError`
- `requests.RequestException`

### Database Operations
- `sqlite3.Error`
- `SQLAlchemyError`
- `psycopg2.Error`

### Data Validation
- `ValueError`
- `TypeError`
- `ValidationError`

### Parsing Operations
- `json.JSONDecodeError`
- `yaml.YAMLError`
- `ParseError`

## 🚫 Anti-Patterns to Avoid

1. **Bare except**: `except:`
2. **Silent failures**: `except: pass`
3. **Too broad**: `except Exception:`
4. **Print in exceptions**: `except: print(...)`
5. **Re-raising without context**: `except: raise`

Generated by Exception Handler Fixer
"""
        
        guidelines_path = Path("docs/EXCEPTION_HANDLING_GUIDELINES.md")
        guidelines_path.parent.mkdir(exist_ok=True)
        
        with open(guidelines_path, 'w', encoding='utf-8') as f:
            f.write(guidelines)
        
        print(f"📝 تم إنشاء دليل Exception Handling: {guidelines_path}")

def main():
    """الدالة الرئيسية"""
    print("🛡️ Exception Handler Fixer")
    print("=" * 50)
    
    fixer = ExceptionHandlerFixer()
    
    # إصلاح المشروع
    results = fixer.fix_project_exceptions()
    
    # إنشاء دليل الممارسات الجيدة
    fixer.create_exception_guidelines()
    
    print(f"\n🎯 تم إصلاح {results['files_fixed']} ملف بـ{results['total_fixes']} إصلاح!")
    print("🛡️ الكود أصبح أكثر أماناً وقابلية للصيانة!")
    
    return results['files_fixed']

if __name__ == "__main__":
    main() 