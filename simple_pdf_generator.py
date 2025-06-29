#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 مولد PDF مبسط - الملفات الأربعة الرئيسية + الرسوم البيانية
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

class SimplePDFGenerator:
    def __init__(self):
        self.output_file = "AI_TEDDY_BEAR_COMPLETE_REPORT_2025.pdf"
        self.setup_styles()
        self.story = []
        self.main_files = ["FULL_AUDIT.md", "ARCHITECTURE.md", "RESTRUCTURE_TREE.md", "REFACTOR_ACTIONS.md"]

    def setup_styles(self):
        self.styles = getSampleStyleSheet()
        
        # إنشاء أنماط مخصصة مع أسماء فريدة
        if 'CustomTitle' not in [s.name for s in self.styles.byName.values()]:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Title'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            ))
        
        if 'CustomSubTitle' not in [s.name for s in self.styles.byName.values()]:
            self.styles.add(ParagraphStyle(
                name='CustomSubTitle',
                parent=self.styles['Heading1'],
                fontSize=14,
                spaceAfter=20,
                textColor=colors.darkgreen
            ))

    def add_cover_page(self):
        title = Paragraph(" مشروع AI Teddy Bear - التحليل الشامل والرسوم البيانية 2025", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        info = f" تاريخ التقرير: {datetime.now().strftime('%d يناير %Y')}"
        self.story.append(Paragraph(info, self.styles['Normal']))
        self.story.append(Spacer(1, 0.3*inch))
        
        summary = """
         محتوى التقرير:
         FULL_AUDIT.md - التدقيق الشامل (247 مشكلة مكتشفة)
         ARCHITECTURE.md - البنية المعمارية المتقدمة
         RESTRUCTURE_TREE.md - خطة إعادة الهيكلة
         REFACTOR_ACTIONS.md - 43 إجراء قابل للتنفيذ
         3 رسوم بيانية تفصيلية مع شروحات
        
         الأولوية: حرجة - تنفيذ فوري مطلوب لأمان الأطفال
        """
        
        summary_para = Paragraph(summary, self.styles['Normal'])
        self.story.append(summary_para)
        self.story.append(PageBreak())

    def process_markdown(self, content):
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                para = Paragraph(f"<b>{title}</b>", self.styles['CustomTitle'])
                self.story.append(para)
                self.story.append(Spacer(1, 0.2*inch))
            elif line.startswith('## '):
                subtitle = line[3:].strip()
                para = Paragraph(f"<b>{subtitle}</b>", self.styles['CustomSubTitle'])
                self.story.append(para)
                self.story.append(Spacer(1, 0.1*inch))
            elif line.startswith('### '):
                subsubtitle = line[4:].strip()
                para = Paragraph(f"<b>{subsubtitle}</b>", self.styles['Heading2'])
                self.story.append(para)
            elif line and not line.startswith('`') and line != '---':
                # تنظيف النص من رموز markdown
                clean_line = line.replace('**', '').replace('*', '')
                para = Paragraph(clean_line, self.styles['Normal'])
                self.story.append(para)
                self.story.append(Spacer(1, 0.05*inch))

    def add_markdown_file(self, filepath):
        if not os.path.exists(filepath):
            print(f" الملف غير موجود: {filepath}")
            return
        
        print(f" معالجة {filepath}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chapter_title = Paragraph(
                f" {os.path.basename(filepath).replace('.md', '').replace('_', ' ').title()}",
                self.styles['CustomTitle']
            )
            self.story.append(chapter_title)
            self.story.append(Spacer(1, 0.3*inch))
            
            self.process_markdown(content)
            self.story.append(PageBreak())
            
        except Exception as e:
            print(f" خطأ في معالجة {filepath}: {e}")

    def add_diagrams(self):
        title = Paragraph(" الرسوم البيانية التفصيلية", self.styles['CustomTitle'])
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))
        
        diagrams = [
            {
                "title": " مخطط معمارية النظام الشامل",
                "explanation": "يوضح البنية الكاملة من ESP32 Teddy Bear إلى خدمات AI والمراقبة الأمنية مع تدفق البيانات عبر جميع الطبقات لضمان استجابة آمنة للطفل.",
                "ascii": """
  AI TEDDY BEAR SYSTEM 
 ‍‍‍ Parent App   API Gateway   Teddy Bear 
                                                    
                                                    
                     Authentication                 
                                                    
                                        
                                                  
               Child   AI   Monitor            
               Mgmt   Engine  System                 
                                                  
                                                  
               Database  AI APIs  Audit         
                                                    
                                        
                                                  
               OpenAI  Hume  ElevenLabs               
                                                    
                                                    
                    Safety Filter                   
                                                    
                                                    
                    Parent Reports                 

"""
            },
            {
                "title": " الجدول الزمني للإجراءات الحرجة",
                "explanation": "مخطط جانت للمهام الحرجة في الأسبوع الأول مع التقدم الحالي ومستويات الأولوية لكل إجراء.",
                "ascii": """
 CRITICAL ACTIONS - WEEK 1 TIMELINE

 Day 1: API Keys      [] 80%      
 Day 1: Audit Log     [] 60%      
 Day 2: Duplicates    [] 40%      
 Day 2: Child Safety  [] 20%      
 Day 3: Memory Opt    [] 0%       
 Day 3: Security      [] 0%       
 Day 4: HTTPS         [] 0%       
 Day 5: Database      [] 0%       
 Day 5: Rate Limit    [] 0%       
 Day 5: Monitoring    [] 0%       

 Status: 1 Complete, 3 In Progress, 6 Pending
 Risk Level: CRITICAL - IMMEDIATE ACTION REQUIRED
"""
            },
            {
                "title": " بنية Clean Architecture المقترحة",
                "explanation": "طبقات Clean Architecture مع فصل واضح بين Domain وApplication وInfrastructure لضمان قابلية الاختبار والصيانة.",
                "ascii": """
 CLEAN ARCHITECTURE LAYERS

           PRESENTATION LAYER              
    (API, Mobile, Web, WebSocket)            

           APPLICATION LAYER               
     (Use Cases, Services, DTOs)             

             DOMAIN LAYER                  
   (Entities, Value Objects, Interfaces)    

         INFRASTRUCTURE LAYER              
  (Database, AI APIs, Storage, Security)    


Key Benefits:
 Dependency Inversion: Outer  Inner layers
 Independent Testing: Each layer isolated
 Technology Agnostic: Easy to swap components
 Business Logic Protection: Domain stays pure
"""
            }
        ]
        
        for i, diagram in enumerate(diagrams, 1):
            # عنوان الرسم
            diagram_title = Paragraph(f"الرسم {i}: {diagram['title']}", self.styles['CustomSubTitle'])
            self.story.append(diagram_title)
            
            # الشرح
            explanation = Paragraph(f"الشرح: {diagram['explanation']}", self.styles['Normal'])
            self.story.append(explanation)
            self.story.append(Spacer(1, 0.2*inch))
            
            # الرسم البياني
            diagram_table = Table([[diagram['ascii']]], colWidths=[6.5*inch])
            diagram_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 2, colors.darkblue),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15)
            ]))
            
            self.story.append(diagram_table)
            self.story.append(Spacer(1, 0.4*inch))

    def generate_pdf(self):
        print(" بدء إنشاء التقرير الشامل...")
        
        doc = SimpleDocTemplate(self.output_file, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        
        self.add_cover_page()
        
        for md_file in self.main_files:
            if os.path.exists(md_file):
                self.add_markdown_file(md_file)
        
        self.add_diagrams()
        
        try:
            doc.build(self.story)
            file_size = os.path.getsize(self.output_file) / 1024 / 1024
            print(f" تم إنشاء التقرير بنجاح!")
            print(f" الملف: {self.output_file}")
            print(f" الحجم: {file_size:.2f} MB")
            print(f" المحتوى: {len(self.main_files)} ملفات + 3 رسوم بيانية")
            return True
        except Exception as e:
            print(f" خطأ: {e}")
            return False

if __name__ == "__main__":
    print(" مولد PDF - الملفات الأربعة الرئيسية + الرسوم البيانية")
    print("=" * 60)
    
    generator = SimplePDFGenerator()
    success = generator.generate_pdf()
    
    if success:
        print("\n تم إنشاء التقرير بنجاح!")
        print(" المحتوى:")
        print("    FULL_AUDIT.md - التدقيق الشامل")
        print("    ARCHITECTURE.md - البنية المعمارية")
        print("    RESTRUCTURE_TREE.md - خطة إعادة الهيكلة")
        print("    REFACTOR_ACTIONS.md - الإجراءات القابلة للتنفيذ")
        print("    3 رسوم بيانية مع شروحات تفصيلية")
    else:
        print(" فشل في إنشاء التقرير")
