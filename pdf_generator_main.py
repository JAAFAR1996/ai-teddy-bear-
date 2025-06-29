#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 مولد PDF شامل - الملفات الأربعة الرئيسية + الرسوم البيانية
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

class MainPDFGenerator:
    def __init__(self):
        self.output_file = "AI_TEDDY_BEAR_MAIN_ANALYSIS_2025.pdf"
        self.setup_styles()
        self.story = []
        
        # الملفات الأربعة الرئيسية فقط
        self.main_files = [
            "FULL_AUDIT.md",
            "ARCHITECTURE.md", 
            "RESTRUCTURE_TREE.md",
            "REFACTOR_ACTIONS.md"
        ]
        
        # الرسوم البيانية مع شروحات مفصلة
        self.diagrams_with_explanations = [
            {
                "title": " مخطط معمارية النظام الشامل",
                "detailed_explanation": """
                هذا المخطط يوضح البنية الكاملة لنظام AI Teddy Bear من منظور شامل:
                
                1. **طبقة المستخدم**: تطبيق الوالدين المحمول والدب الذكي ESP32
                2. **طبقة البوابة**: API Gateway يدير جميع الطلبات والاستجابات
                3. **طبقة الخدمات**: خدمات المصادقة وإدارة الأطفال ومحرك الذكاء الاصطناعي
                4. **طبقة الذكاء الاصطناعي**: خدمات متعددة (OpenAI, Hume AI, ElevenLabs, Whisper)
                5. **طبقة الحماية**: فلاتر الأمان وتحليل سلوك الأطفال
                6. **طبقة المراقبة**: نظام التدقيق ولوحة الأمان وتقارير الوالدين
                
                يظهر المخطط كيف تتدفق البيانات من الدب الذكي عبر جميع الطبقات
                لضمان استجابة آمنة ومناسبة للطفل.
                """,
                "ascii_diagram": '''
  AI TEDDY BEAR SYSTEM OVERVIEW 
                                                                        
  ‍‍‍ Parent Mobile App      ESP32 Teddy Bear           
                                                                     
                                                                     
                               Cloud API Gateway                     
                                                                      
                                
                                                                    
               Authentication    Child Mgmt     AI Engine         
                                 Service                             
                                                                   
            ‍‍‍ Parent DB                   AI Services          
                                                                      
                               Child Profiles                   
                                  Database                           
                                                                     
                    
      OpenAI GPT-4   Hume AI Emotion                           
      ElevenLabs TTS   Whisper STT                            
                    
                                                                      
                                               Content Safety       
                                                 Filter                
                                                                      
                                                                      
                                               Child Behavior        
                                                 Analyzer              
                                                                      
                    
                                                                     
             Audit & Monitoring               Security Dashboard   
                                                                     
                                                                     
             Parent Reports              ‍ Security Alerts        
                                                                        

'''
            },
            {
                "title": " الجدول الزمني للإجراءات الحرجة - الأسبوع الأول",
                "detailed_explanation": """
                مخطط جانت يوضح التسلسل الزمني للإجراءات الحرجة في الأسبوع الأول:
                
                **اليوم الأول (الإجراءات الفورية):**
                - إلغاء API Keys المكشوفة (30 دقيقة) - مكتمل 80%
                - تفعيل نظام Audit Logging (1 ساعة) - مكتمل 60%
                
                **اليوم الثاني (الحماية الأساسية):**
                - إزالة الملفات والمجلدات المكررة (2 ساعة) - مكتمل 40%
                - تفعيل فلترة محتوى الأطفال (3 ساعات) - مكتمل 20%
                
                **اليوم الثالث (التحسينات):**
                - تحسين استخدام الذاكرة (4 ساعات) - لم يبدأ
                - إضافة Security Headers (1 ساعة) - لم يبدأ
                
                **اليوم الرابع (التأمين):**
                - فرض HTTPS على جميع الاتصالات (2 ساعة) - لم يبدأ
                
                **اليوم الخامس (قاعدة البيانات):**
                - تشفير قاعدة البيانات (6 ساعات) - لم يبدأ
                - تطبيق Rate Limiting (2 ساعة) - لم يبدأ
                - تفعيل Emergency Monitoring (1 ساعة) - لم يبدأ
                """,
                "ascii_diagram": '''
 CRITICAL ACTIONS TIMELINE - WEEK 1 (Hour by Hour)

 Day 1: API Keys Revocation      [] 80%  URGENT     
        (30 min) - COMPLETED                                          
                                                                      
 Day 1: Audit Logging Enable     [] 60%  IN PROGRESS
        (1 hour) - PRIORITY                                           
                                                                      
 Day 2: Remove Duplicates        [] 40%  STARTED    
        (2 hours) - CLEANUP                                           
                                                                      
 Day 2: Child Safety Filter      [] 20%  CRITICAL   
        (3 hours) - CHILD PROTECTION                                  
                                                                      
 Day 3: Memory Optimization      [] 0%   PENDING    
        (4 hours) - PERFORMANCE                                       
                                                                      
 Day 3: Security Headers         [] 0%   PENDING    
        (1 hour) - SECURITY                                           
                                                                      
 Day 4: HTTPS Enforcement        [] 0%   PENDING    
        (2 hours) - COMMUNICATION                                     
                                                                      
 Day 5: Database Encryption      [] 0%   PENDING    
        (6 hours) - DATA PROTECTION                                   
                                                                      
 Day 5: Rate Limiting            [] 0%   PENDING    
        (2 hours) - API PROTECTION                                    
                                                                      
 Day 5: Emergency Monitoring     [] 0%   PENDING    
        (1 hour) - SYSTEM WATCH                                       


 PROGRESS SUMMARY:
  Completed: 1 task (API Keys)
  In Progress: 3 tasks (Audit, Cleanup, Safety)  
  Pending: 6 tasks (remaining critical items)
  Total Risk Level: CRITICAL - IMMEDIATE ACTION REQUIRED
'''
            },
            {
                "title": " بنية Clean Architecture المقترحة",
                "detailed_explanation": """
                هذا المخطط يوضح طبقات Clean Architecture المقترحة للنظام:
                
                **طبقة العرض (Presentation Layer):**
                - تحتوي على واجهات المستخدم: API REST، تطبيقات الويب والمحمول، WebSocket
                - مسؤولة عن التفاعل مع المستخدمين النهائيين
                - تحول طلبات المستخدم إلى استدعاءات للطبقة التطبيقية
                
                **طبقة التطبيق (Application Layer):**
                - تحتوي على Use Cases وخدمات التطبيق وكائنات نقل البيانات (DTOs)
                - تنسق بين الطبقات المختلفة
                - تحتوي على منطق التطبيق وتدفق العمليات
                
                **طبقة النطاق (Domain Layer):**
                - قلب النظام يحتوي على Entities وValue Objects والواجهات
                - تحتوي على منطق الأعمال الأساسي
                - مستقلة تماماً عن التقنيات الخارجية
                
                **طبقة البنية التحتية (Infrastructure Layer):**
                - تحتوي على التفاصيل التقنية: قواعد البيانات، APIs الخارجية، التخزين، الأمان
                - تنفذ الواجهات المعرفة في طبقة النطاق
                - تتعامل مع العالم الخارجي
                
                **مبدأ Dependency Inversion:**
                الطبقات الخارجية تعتمد على الطبقات الداخلية، وليس العكس
                """,
                "ascii_diagram": '''
 CLEAN ARCHITECTURE LAYERS - AI TEDDY BEAR SYSTEM

                                                                      
   PRESENTATION LAYER  
                                                                    
    REST API      Mobile App      Web App      WebSocket    
                                                                    
    API Endpoints     UI Components     Real-time Handlers    
                                                                    
  
                                                                      
                                                                      
   APPLICATION LAYER  
                                                                    
    Use Cases:                                                    
    ProcessChildInput           GenerateAIResponse           
    ManageConversation          AnalyzeChildEmotion          
    ValidateChildSafety         CreateParentReport           
                                                                    
    Services:                     DTOs:                        
    AIOrchestrator              ConversationRequest          
    AudioProcessor              AIResponse                   
    ConversationManager         SafetyAnalysis              
                                                                    
  
                                                                      
                                                                      
   DOMAIN LAYER (CORE)  
                                                                    
    Entities:                     Value Objects:               
    Child                        DeviceId (UDID)             
    Conversation                 AudioData                   
    Message                      EmotionScore                
    ParentProfile                SafetyLevel                 
                                                                    
    Interfaces:                   Domain Services:             
    IChildRepository             EmotionAnalyzer             
    IAIService                   ContentModerator            
    IAudioProcessor              ChildSafetyValidator        
                                                                    
  
                                                                      
                                                                      
   INFRASTRUCTURE LAYER  
                                                                    
    Data Persistence:            External AI APIs:             
    SqliteChildRepository       OpenAIClient (GPT-4)         
    ConversationDatabase        HumeAIClient (Emotions)      
    AuditLogStorage             ElevenLabsClient (TTS)        
                                   WhisperClient (STT)           
    Security Systems:            File Storage:                  
    AuthenticationService       AudioFileStorage             
    EncryptionService           ConversationArchive          
    AuditLogger                ParentReportStorage           
                                                                    
  
                                                                      


 KEY PRINCIPLES:
  Dependency Inversion: Outer layers depend on inner layers
  Single Responsibility: Each layer has one clear purpose  
  Independence: Domain layer is completely isolated
  Testability: Each layer can be tested independently
'''
            }
        ]

    def setup_styles(self):
        """إعداد أنماط النص المتقدمة"""
        self.styles = getSampleStyleSheet()
        
        # نمط العنوان الرئيسي
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # نمط العنوان الفرعي
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            spaceBefore=15,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        ))
        
        # نمط النص العادي
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # نمط للشروحات
        self.styles.add(ParagraphStyle(
            name='Explanation',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            textColor=colors.darkslategray,
            leftIndent=20,
            rightIndent=20
        ))

    def add_cover_page(self):
        """صفحة الغلاف"""
        
        # العنوان الرئيسي
        title = Paragraph(
            " مشروع AI Teddy Bear<br/>التحليل الشامل والرسوم البيانية 2025",
            self.styles['MainTitle']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        # معلومات المشروع
        project_info = [
            [" نوع التقرير:", "تحليل شامل مع رسوم بيانية"],
            [" تاريخ:", datetime.now().strftime("%d يناير %Y")],
            [" المحتوى:", "4 ملفات رئيسية + 3 رسوم بيانية"],
            [" السرية:", "سري - للإدارة العليا"],
            [" الأولوية:", "حرجة - تنفيذ فوري"]
        ]
        
        table = Table(project_info, colWidths=[2*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
        
        # ملخص سريع
        summary = """
        <b> ملخص المحتوى:</b><br/><br/>
         <b>FULL_AUDIT.md:</b> تدقيق شامل كشف 247 مشكلة حرجة<br/>
         <b>ARCHITECTURE.md:</b> البنية المعمارية المتقدمة<br/>
         <b>RESTRUCTURE_TREE.md:</b> خطة إعادة الهيكلة<br/>
         <b>REFACTOR_ACTIONS.md:</b> 43 إجراء قابل للتنفيذ<br/><br/>
         <b>3 رسوم بيانية مفصلة:</b> معمارية النظام، الجدول الزمني، Clean Architecture<br/><br/>
         <b>التوصية:</b> بدء التنفيذ فوراً لأمان الأطفال والامتثال القانوني
        """
        
        summary_para = Paragraph(summary, self.styles['BodyText'])
        self.story.append(summary_para)
        self.story.append(PageBreak())

    def convert_markdown_to_pdf(self, content):
        """تحويل محتوى Markdown إلى عناصر PDF"""
        
        lines = content.split('\n')
        current_para = ""
        in_code_block = False
        
        for line in lines:
            line = line.strip()
            
            # معالجة code blocks
            if line.startswith('`'):
                if in_code_block:
                    # نهاية code block
                    if current_para:
                        code_table = Table([[current_para]], colWidths=[6*inch])
                        code_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                            ('TOPPADDING', (0, 0), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
                        ]))
                        self.story.append(code_table)
                        self.story.append(Spacer(1, 0.1*inch))
                        current_para = ""
                    in_code_block = False
                else:
                    # بداية code block
                    if current_para:
                        para = Paragraph(current_para, self.styles['BodyText'])
                        self.story.append(para)
                        current_para = ""
                    in_code_block = True
                continue
            
            if in_code_block:
                current_para += line + "\n"
                continue
            
            # معالجة العناوين
            if line.startswith('# '):
                if current_para:
                    para = Paragraph(current_para, self.styles['BodyText'])
                    self.story.append(para)
                    current_para = ""
                
                title = line[2:].strip()
                title_para = Paragraph(f"<b>{title}</b>", self.styles['MainTitle'])
                self.story.append(title_para)
                self.story.append(Spacer(1, 0.2*inch))
                
            elif line.startswith('## '):
                if current_para:
                    para = Paragraph(current_para, self.styles['BodyText'])
                    self.story.append(para)
                    current_para = ""
                
                subtitle = line[3:].strip()
                subtitle_para = Paragraph(f"<b>{subtitle}</b>", self.styles['SubTitle'])
                self.story.append(subtitle_para)
                
            elif line.startswith('### '):
                if current_para:
                    para = Paragraph(current_para, self.styles['BodyText'])
                    self.story.append(para)
                    current_para = ""
                
                subsubtitle = line[4:].strip()
                subsubtitle_para = Paragraph(f"<b>{subsubtitle}</b>", self.styles['Heading2'])
                self.story.append(subsubtitle_para)
                
            elif line == '---':
                # فاصل صفحة
                if current_para:
                    para = Paragraph(current_para, self.styles['BodyText'])
                    self.story.append(para)
                    current_para = ""
                self.story.append(PageBreak())
                
            elif line:
                # نص عادي
                # تنظيف النص من رموز Markdown الشائعة
                cleaned_line = line.replace('**', '<b>').replace('**', '</b>')
                cleaned_line = cleaned_line.replace('*', '<i>').replace('*', '</i>')
                current_para += cleaned_line + "<br/>"
        
        # إضافة آخر فقرة
        if current_para:
            para = Paragraph(current_para, self.styles['BodyText'])
            self.story.append(para)

    def add_markdown_file(self, filepath):
        """إضافة ملف Markdown"""
        
        if not os.path.exists(filepath):
            print(f" الملف غير موجود: {filepath}")
            return
        
        print(f" معالجة {filepath}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # إضافة عنوان الفصل
            chapter_title = Paragraph(
                f" {os.path.basename(filepath).replace('.md', '').replace('_', ' ').title()}",
                self.styles['MainTitle']
            )
            self.story.append(chapter_title)
            self.story.append(Spacer(1, 0.3*inch))
            
            # تحويل المحتوى
            self.convert_markdown_to_pdf(content)
            self.story.append(PageBreak())
            
        except Exception as e:
            print(f" خطأ في معالجة {filepath}: {e}")

    def add_diagrams_with_detailed_explanations(self):
        """إضافة الرسوم البيانية مع شروحات مفصلة"""
        
        # عنوان القسم
        diagrams_title = Paragraph(" الرسوم البيانية التفصيلية", self.styles['MainTitle'])
        self.story.append(diagrams_title)
        self.story.append(Spacer(1, 0.3*inch))
        
        intro_text = """
        يحتوي هذا القسم على الرسوم البيانية الثلاثة الأساسية للمشروع مع شروحات تفصيلية 
        لكل رسم وأهميته في فهم النظام وتطويره وتحسينه.
        """
        
        intro_para = Paragraph(intro_text, self.styles['Explanation'])
        self.story.append(intro_para)
        self.story.append(Spacer(1, 0.3*inch))
        
        # إضافة كل رسم بياني مع شرحه المفصل
        for i, diagram in enumerate(self.diagrams_with_explanations, 1):
            
            # عنوان الرسم
            diagram_title = Paragraph(
                f"الرسم البياني {i}: {diagram['title']}", 
                self.styles['SubTitle']
            )
            self.story.append(diagram_title)
            self.story.append(Spacer(1, 0.1*inch))
            
            # الشرح التفصيلي
            explanation_para = Paragraph(
                diagram['detailed_explanation'], 
                self.styles['Explanation']
            )
            self.story.append(explanation_para)
            self.story.append(Spacer(1, 0.2*inch))
            
            # الرسم البياني ASCII
            diagram_table = Table([[diagram['ascii_diagram']]], colWidths=[7*inch])
            diagram_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 2, colors.darkblue),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10)
            ]))
            
            self.story.append(diagram_table)
            self.story.append(Spacer(1, 0.4*inch))
            
            # فاصل بين الرسوم
            if i < len(self.diagrams_with_explanations):
                separator = Paragraph("" * 80, self.styles['BodyText'])
                self.story.append(separator)
                self.story.append(Spacer(1, 0.3*inch))

    def generate_pdf(self):
        """إنشاء ملف PDF النهائي"""
        
        print(" بدء إنشاء التقرير الشامل مع الرسوم البيانية...")
        
        # إنشاء المستند
        doc = SimpleDocTemplate(
            self.output_file,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=30
        )
        
        # إضافة المحتوى
        print(" إضافة صفحة الغلاف...")
        self.add_cover_page()
        
        # إضافة الملفات الأربعة الرئيسية
        for md_file in self.main_files:
            if os.path.exists(md_file):
                self.add_markdown_file(md_file)
            else:
                print(f" الملف غير موجود: {md_file}")
        
        # إضافة الرسوم البيانية مع الشروحات
        print(" إضافة الرسوم البيانية مع الشروحات التفصيلية...")
        self.add_diagrams_with_detailed_explanations()
        
        # بناء PDF
        print(" بناء ملف PDF...")
        try:
            doc.build(self.story)
            file_size = os.path.getsize(self.output_file) / 1024 / 1024
            print(f" تم إنشاء التقرير بنجاح!")
            print(f" اسم الملف: {self.output_file}")
            print(f" حجم الملف: {file_size:.2f} MB")
            print(f" المحتوى: {len(self.main_files)} ملفات MD + {len(self.diagrams_with_explanations)} رسوم بيانية")
            
            return True
            
        except Exception as e:
            print(f" خطأ في إنشاء PDF: {e}")
            return False

def main():
    """الدالة الرئيسية"""
    
    print(" مولد PDF للملفات الأربعة الرئيسية + الرسوم البيانية")
    print("=" * 70)
    
    generator = MainPDFGenerator()
    
    # فحص وجود الملفات
    missing_files = []
    for md_file in generator.main_files:
        if not os.path.exists(md_file):
            missing_files.append(md_file)
    
    if missing_files:
        print(" الملفات التالية غير موجودة:")
        for file in missing_files:
            print(f"   - {file}")
        print(" سيتم إنشاء التقرير بالملفات المتاحة فقط")
    
    # إنشاء التقرير
    success = generator.generate_pdf()
    
    if success:
        print("\n تم إنشاء التقرير الشامل بنجاح!")
        print(" يحتوي التقرير على:")
        print("    صفحة غلاف احترافية")
        print("    الملفات الأربعة الرئيسية (FULL_AUDIT, ARCHITECTURE, RESTRUCTURE_TREE, REFACTOR_ACTIONS)")
        print("    3 رسوم بيانية مفصلة مع شروحات شاملة:")
        print("       مخطط معمارية النظام الشامل")
        print("       الجدول الزمني للإجراءات الحرجة")
        print("       بنية Clean Architecture المقترحة")
        print("    تنسيق احترافي مع جداول وألوان")
        
    else:
        print("\n فشل في إنشاء التقرير")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
