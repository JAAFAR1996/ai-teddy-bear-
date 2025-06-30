import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

/**
 * 🎯 PDF Export Utilities for AI Teddy Bear Dashboard
 * Professional PDF generation for parent reports
 */

// Configuration constants
const PDF_CONFIG = {
  format: 'a4',
  orientation: 'portrait',
  unit: 'mm',
  compress: true,
  precision: 2,
  margins: {
    top: 20,
    right: 20,
    bottom: 20,
    left: 20
  },
  fonts: {
    primary: 'helvetica',
    arabic: 'NotoSansArabic-Regular', // Better Arabic font support
    fallback: 'arial'
  },
  colors: {
    primary: '#3B82F6',
    secondary: '#6B7280',
    text: '#1F2937',
    lightGray: '#F3F4F6',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444'
  },
  // Enhanced quality settings
  quality: {
    dpi: 300,
    scale: 3, // Higher scale for better quality
    compression: 0.92,
    format: 'PNG'
  }
};

/**
 * Convert HTML element to PDF using html2canvas + jsPDF
 * @param {HTMLElement} element - DOM element to convert
 * @param {Object} options - Configuration options
 * @returns {Promise<Blob>} PDF blob
 */
export const htmlToPDF = async (element, options = {}) => {
  const {
    filename = 'report',
    orientation = 'portrait',
    format = 'a4',
    quality = PDF_CONFIG.quality.compression,
    backgroundColor = '#ffffff',
    scale = PDF_CONFIG.quality.scale, // Use enhanced scale
    useCORS = true,
    allowTaint = true,
    dpi = PDF_CONFIG.quality.dpi,
    ...canvasOptions
  } = options;

  try {
    // Enhanced canvas generation with higher quality
    const canvas = await html2canvas(element, {
      scale,
      useCORS,
      allowTaint,
      backgroundColor,
      logging: false,
      width: element.scrollWidth,
      height: element.scrollHeight,
      // Enhanced quality settings
      foreignObjectRendering: true,
      removeContainer: true,
      ignoreElements: (element) => {
        // Skip problematic elements
        return element.classList.contains('no-pdf') || 
               element.tagName === 'IFRAME';
      },
      onclone: (clonedDoc) => {
        // Optimize fonts for PDF
        const style = clonedDoc.createElement('style');
        style.textContent = `
          * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
          }
          @font-face {
            font-family: 'NotoSansArabic';
            src: url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;600;700&display=swap');
          }
        `;
        clonedDoc.head.appendChild(style);
      },
      ...canvasOptions
    });

    // Calculate dimensions with better precision
    const imgWidth = 210; // A4 width in mm
    const pageHeight = 295; // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;

    // Create PDF with enhanced settings
    const pdf = new jsPDF({
      orientation,
      unit: 'mm',
      format,
      compress: true,
      precision: PDF_CONFIG.precision
    });

    // Add Arabic font support
    try {
      pdf.setFont(PDF_CONFIG.fonts.arabic);
    } catch (fontError) {
      console.warn('Arabic font not available, using fallback');
      pdf.setFont(PDF_CONFIG.fonts.fallback);
    }

    // Generate high-quality image data
    const imgData = canvas.toDataURL(`image/${PDF_CONFIG.quality.format.toLowerCase()}`, quality);
    let position = 0;

    // Add first page
    pdf.addImage(
      imgData, 
      PDF_CONFIG.quality.format, 
      0, 
      position, 
      imgWidth, 
      imgHeight,
      undefined,
      'FAST' // Compression mode
    );
    heightLeft -= pageHeight;

    // Add additional pages if needed
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(
        imgData, 
        PDF_CONFIG.quality.format, 
        0, 
        position, 
        imgWidth, 
        imgHeight,
        undefined,
        'FAST'
      );
      heightLeft -= pageHeight;
    }

    return pdf.output('blob');
  } catch (error) {
    console.error('PDF generation failed:', error);
    throw new Error(`فشل في إنشاء ملف PDF: ${error.message}`);
  }
};

/**
 * Generate professional child report PDF
 * @param {Object} childData - Child information and analytics
 * @param {Object} options - PDF generation options
 * @returns {Promise<Blob>} Generated PDF blob
 */
export const generateChildReport = async (childData, options = {}) => {
  const {
    format = 'a4',
    orientation = 'portrait',
    includeCharts = true,
    includeTimeline = true,
    dateRange = '7d',
    template = 'detailed'
  } = options;

  try {
    const pdf = new jsPDF({
      orientation,
      unit: 'mm',
      format,
      compress: true
    });

    // Set up fonts and colors
    pdf.setFont(PDF_CONFIG.fonts.primary);
    
    // Page 1: Cover & Summary
    await addCoverPage(pdf, childData);
    
    // Page 2: Statistics & Overview
    pdf.addPage();
    await addStatisticsPage(pdf, childData);
    
    // Page 3: Emotion Analysis (if data available)
    if (childData.emotions && includeCharts) {
      pdf.addPage();
      await addEmotionAnalysisPage(pdf, childData);
    }
    
    // Page 4: Activity Timeline (if requested)
    if (childData.activities && includeTimeline) {
      pdf.addPage();
      await addTimelinePage(pdf, childData);
    }
    
    // Page 5: Recommendations & Tips
    pdf.addPage();
    await addRecommendationsPage(pdf, childData);

    return pdf.output('blob');
  } catch (error) {
    console.error('Report generation failed:', error);
    throw new Error(`فشل في إنشاء التقرير: ${error.message}`);
  }
};

/**
 * Add cover page to PDF with enhanced Arabic font support
 */
const addCoverPage = async (pdf, childData) => {
  const { child, reportDate, summary } = childData;
  
  // Set up Arabic font support
  try {
    pdf.setFont(PDF_CONFIG.fonts.arabic);
  } catch (fontError) {
    console.warn('Arabic font not available, using fallback');
    pdf.setFont(PDF_CONFIG.fonts.fallback);
  }
  
  // Header with enhanced gradient effect
  pdf.setFillColor(PDF_CONFIG.colors.primary);
  pdf.rect(0, 0, 210, 40, 'F');
  
  // Add subtle gradient effect
  pdf.setFillColor('#60A5FA'); // Lighter blue
  pdf.rect(0, 0, 210, 20, 'F');
  
  // Title with better Arabic rendering
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(24);
  pdf.setFont(PDF_CONFIG.fonts.arabic, 'bold');
  pdf.text('🧸 تقرير دب تيدي الذكي', 105, 20, { 
    align: 'center',
    renderingMode: 'fill',
    charSpace: 0.1
  });
  
  pdf.setFontSize(14);
  pdf.setFont(PDF_CONFIG.fonts.arabic, 'normal');
  pdf.text('تقرير شامل عن تطور ونمو الطفل', 105, 30, { 
    align: 'center',
    renderingMode: 'fill'
  });
  
  // Child information section
  pdf.setTextColor(PDF_CONFIG.colors.text);
  pdf.setFontSize(18);
  pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
  pdf.text('معلومات الطفل', 20, 60);
  
  // Child details
  pdf.setFontSize(12);
  pdf.setFont(PDF_CONFIG.fonts.primary, 'normal');
  pdf.text(`الاسم: ${child.name || 'غير محدد'}`, 20, 75);
  pdf.text(`العمر: ${child.age || 'غير محدد'} سنوات`, 20, 85);
  pdf.text(`تاريخ التقرير: ${new Date(reportDate || Date.now()).toLocaleDateString('ar-SA')}`, 20, 95);
  pdf.text(`فترة التقرير: آخر 7 أيام`, 20, 105);
  
  // Summary statistics
  if (summary) {
    pdf.setFontSize(16);
    pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
    pdf.text('ملخص سريع', 20, 130);
    
    // Statistics boxes
    const stats = [
      { label: 'إجمالي المحادثات', value: summary.totalConversations || 0, color: PDF_CONFIG.colors.primary },
      { label: 'الحالة العاطفية', value: summary.emotionScore || 'ممتاز', color: PDF_CONFIG.colors.success },
      { label: 'وقت النشاط', value: `${summary.activeMinutes || 45} دقيقة`, color: PDF_CONFIG.colors.warning },
      { label: 'مستوى التعلم', value: summary.learningProgress || '85%', color: PDF_CONFIG.colors.primary }
    ];
    
    let yPos = 150;
    stats.forEach((stat, index) => {
      const xPos = 20 + (index % 2) * 90;
      if (index % 2 === 0 && index > 0) yPos += 35;
      
      // Box background
      pdf.setFillColor(stat.color + '22');
      pdf.rect(xPos, yPos - 5, 80, 25, 'F');
      
      // Stat label and value
      pdf.setFontSize(10);
      pdf.setTextColor(PDF_CONFIG.colors.secondary);
      pdf.text(stat.label, xPos + 5, yPos + 3);
      
      pdf.setFontSize(14);
      pdf.setTextColor(PDF_CONFIG.colors.text);
      pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
      pdf.text(String(stat.value), xPos + 5, yPos + 15);
    });
  }
  
  // Footer note
  pdf.setFontSize(10);
  pdf.setTextColor(PDF_CONFIG.colors.secondary);
  pdf.text('هذا التقرير تم إنشاؤه تلقائياً بواسطة نظام دب تيدي الذكي', 105, 280, { align: 'center' });
  pdf.text(`تاريخ الإنشاء: ${new Date().toLocaleString('ar-SA')}`, 105, 290, { align: 'center' });
};

/**
 * Add statistics page to PDF
 */
const addStatisticsPage = async (pdf, childData) => {
  const { stats, trends } = childData;
  
  // Page title
  pdf.setFontSize(20);
  pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
  pdf.setTextColor(PDF_CONFIG.colors.text);
  pdf.text('📊 الإحصائيات والتحليلات', 20, 30);
  
  // Weekly trends section
  if (trends) {
    pdf.setFontSize(14);
    pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
    pdf.text('اتجاهات الأسبوع', 20, 50);
    
    // Trend items
    let yPos = 65;
    const trendItems = [
      { label: 'التفاعل اليومي', value: trends.dailyInteraction || '+12%', trend: 'up' },
      { label: 'الاستقرار العاطفي', value: trends.emotionalStability || '+8%', trend: 'up' },
      { label: 'التعلم والنمو', value: trends.learningGrowth || '+15%', trend: 'up' },
      { label: 'وقت النشاط', value: trends.activityTime || '+5 دقائق', trend: 'up' }
    ];
    
    trendItems.forEach((item, index) => {
      // Trend icon
      const trendIcon = item.trend === 'up' ? '📈' : item.trend === 'down' ? '📉' : '➡️';
      const trendColor = item.trend === 'up' ? PDF_CONFIG.colors.success : 
                        item.trend === 'down' ? PDF_CONFIG.colors.danger : PDF_CONFIG.colors.secondary;
      
      pdf.setFontSize(12);
      pdf.setTextColor(PDF_CONFIG.colors.text);
      pdf.text(`${trendIcon} ${item.label}`, 25, yPos);
      
      pdf.setTextColor(trendColor);
      pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
      pdf.text(item.value, 150, yPos);
      
      pdf.setFont(PDF_CONFIG.fonts.primary, 'normal');
      yPos += 15;
    });
  }
  
  // Activity breakdown
  pdf.setFontSize(14);
  pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
  pdf.setTextColor(PDF_CONFIG.colors.text);
  pdf.text('تفصيل الأنشطة', 20, 150);
  
  if (stats && stats.activities) {
    let yPos = 165;
    Object.entries(stats.activities).forEach(([activity, count]) => {
      pdf.setFontSize(11);
      pdf.setTextColor(PDF_CONFIG.colors.text);
      pdf.text(`• ${activity}`, 25, yPos);
      pdf.text(`${count} مرة`, 150, yPos);
      yPos += 12;
    });
  }
};

/**
 * Add emotion analysis page to PDF
 */
const addEmotionAnalysisPage = async (pdf, childData) => {
  const { emotions } = childData;
  
  // Page title
  pdf.setFontSize(20);
  pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
  pdf.setTextColor(PDF_CONFIG.colors.text);
  pdf.text('❤️ تحليل المشاعر', 20, 30);
  
  if (emotions && emotions.summary) {
    // Emotion summary
    pdf.setFontSize(12);
    pdf.setFont(PDF_CONFIG.fonts.primary, 'normal');
    pdf.text('الحالة العاطفية العامة للطفل خلال الفترة المحددة:', 20, 50);
    
    // Dominant emotion
    const dominantEmotion = emotions.summary.dominant || 'سعيد';
    const emotionEmoji = {
      'سعيد': '😊',
      'حماس': '🤩',
      'هدوء': '😌',
      'فضول': '🤔',
      'حزن': '😢'
    }[dominantEmotion] || '😊';
    
    pdf.setFontSize(16);
    pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
    pdf.setTextColor(PDF_CONFIG.colors.success);
    pdf.text(`${emotionEmoji} المشاعر السائدة: ${dominantEmotion}`, 20, 70);
    
    // Emotion breakdown
    if (emotions.breakdown) {
      pdf.setFontSize(14);
      pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
      pdf.setTextColor(PDF_CONFIG.colors.text);
      pdf.text('توزيع المشاعر:', 20, 95);
      
      let yPos = 110;
      Object.entries(emotions.breakdown).forEach(([emotion, percentage]) => {
        const emotionEmojis = {
          joy: '😊',
          happiness: '😄',
          excitement: '🤩',
          curiosity: '🤔',
          calm: '😌',
          sadness: '😢'
        };
        
        const emoji = emotionEmojis[emotion] || '😐';
        const arabicEmotion = {
          joy: 'فرح',
          happiness: 'سعادة',
          excitement: 'حماس',
          curiosity: 'فضول',
          calm: 'هدوء',
          sadness: 'حزن'
        }[emotion] || emotion;
        
        // Progress bar
        const barWidth = (percentage / 100) * 120;
        pdf.setFillColor(PDF_CONFIG.colors.lightGray);
        pdf.rect(80, yPos - 3, 120, 6, 'F');
        
        const barColor = percentage > 60 ? PDF_CONFIG.colors.success : 
                        percentage > 30 ? PDF_CONFIG.colors.warning : PDF_CONFIG.colors.secondary;
        pdf.setFillColor(barColor);
        pdf.rect(80, yPos - 3, barWidth, 6, 'F');
        
        // Label and percentage
        pdf.setFontSize(11);
        pdf.setTextColor(PDF_CONFIG.colors.text);
        pdf.text(`${emoji} ${arabicEmotion}`, 25, yPos);
        pdf.text(`${Math.round(percentage)}%`, 205, yPos);
        
        yPos += 15;
      });
    }
  }
};

/**
 * Add timeline page to PDF
 */
const addTimelinePage = async (pdf, childData) => {
  const { activities } = childData;
  
  // Page title
  pdf.setFontSize(20);
  pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
  pdf.setTextColor(PDF_CONFIG.colors.text);
  pdf.text('📝 جدول الأنشطة', 20, 30);
  
  if (activities && activities.length > 0) {
    pdf.setFontSize(12);
    pdf.text('آخر الأنشطة والتفاعلات:', 20, 50);
    
    let yPos = 70;
    activities.slice(0, 10).forEach((activity, index) => {
      // Activity icon
      const activityIcons = {
        conversation: '💬',
        achievement: '🏆',
        learning: '📚',
        play: '🎮'
      };
      const icon = activityIcons[activity.type] || '📝';
      
      // Date
      const date = new Date(activity.timestamp || activity.date);
      const timeStr = date.toLocaleDateString('ar-SA', { 
        day: 'numeric', 
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      });
      
      // Activity info
      pdf.setFontSize(10);
      pdf.setTextColor(PDF_CONFIG.colors.secondary);
      pdf.text(timeStr, 20, yPos);
      
      pdf.setFontSize(11);
      pdf.setTextColor(PDF_CONFIG.colors.text);
      pdf.text(`${icon} ${activity.title || activity.message || 'نشاط'}`, 60, yPos);
      
      if (activity.emotion) {
        const emotionEmojis = {
          joy: '😊', happiness: '😄', excitement: '🤩',
          curiosity: '🤔', calm: '😌', sadness: '😢'
        };
        const emoji = emotionEmojis[activity.emotion] || '😐';
        pdf.text(emoji, 180, yPos);
      }
      
      yPos += 12;
      
      // Page break if needed
      if (yPos > 260 && index < activities.length - 1) {
        pdf.addPage();
        yPos = 30;
      }
    });
  }
};

/**
 * Add recommendations page to PDF
 */
const addRecommendationsPage = async (pdf, childData) => {
  const { recommendations, tips } = childData;
  
  // Page title
  pdf.setFontSize(20);
  pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
  pdf.setTextColor(PDF_CONFIG.colors.text);
  pdf.text('💡 التوصيات والنصائح', 20, 30);
  
  // Recommendations section
  if (recommendations && recommendations.length > 0) {
    pdf.setFontSize(14);
    pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
    pdf.text('توصيات مخصصة لطفلك:', 20, 50);
    
    let yPos = 65;
    recommendations.forEach((rec, index) => {
      pdf.setFontSize(11);
      pdf.setTextColor(PDF_CONFIG.colors.text);
      pdf.text(`${index + 1}. ${rec.text || rec}`, 25, yPos);
      yPos += 15;
    });
  }
  
  // General tips
  const generalTips = tips || [
    'احرص على التفاعل اليومي مع طفلك',
    'شجع الطفل على التعبير عن مشاعره',
    'استخدم اللعب كوسيلة للتعلم',
    'احتفل بالإنجازات الصغيرة',
    'حافظ على روتين يومي مستقر'
  ];
  
  pdf.setFontSize(14);
  pdf.setFont(PDF_CONFIG.fonts.primary, 'bold');
  pdf.text('نصائح عامة:', 20, 150);
  
  let yPos = 165;
  generalTips.forEach((tip, index) => {
    pdf.setFontSize(11);
    pdf.setTextColor(PDF_CONFIG.colors.text);
    pdf.text(`• ${tip}`, 25, yPos);
    yPos += 15;
  });
  
  // Footer
  pdf.setFontSize(10);
  pdf.setTextColor(PDF_CONFIG.colors.secondary);
  pdf.text('تم إنشاء هذا التقرير بواسطة الذكاء الاصطناعي لدب تيدي', 105, 280, { align: 'center' });
};

/**
 * Download PDF file
 * @param {Blob} pdfBlob - PDF blob
 * @param {String} filename - File name
 */
export const downloadPDF = (pdfBlob, filename = 'report.pdf') => {
  try {
    const url = URL.createObjectURL(pdfBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up
    setTimeout(() => URL.revokeObjectURL(url), 100);
    
    return true;
  } catch (error) {
    console.error('Download failed:', error);
    return false;
  }
};

/**
 * Preview PDF in new tab
 * @param {Blob} pdfBlob - PDF blob
 */
export const previewPDF = (pdfBlob) => {
  try {
    const url = URL.createObjectURL(pdfBlob);
    const newWindow = window.open(url, '_blank');
    
    if (!newWindow) {
      throw new Error('Popup blocked');
    }
    
    // Clean up after a delay
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    
    return true;
  } catch (error) {
    console.error('Preview failed:', error);
    return false;
  }
};

/**
 * Export dashboard as PDF
 * @param {String} elementId - Dashboard element ID
 * @param {Object} childData - Child data for report
 * @param {Object} options - Export options
 */
export const exportDashboardPDF = async (elementId, childData, options = {}) => {
  const {
    filename = `تقرير-${childData.child?.name || 'طفل'}-${new Date().toISOString().split('T')[0]}.pdf`,
    method = 'professional', // 'screenshot' or 'professional'
    includeCharts = true,
    includeTimeline = true
  } = options;

  try {
    let pdfBlob;
    
    if (method === 'professional') {
      // Generate professional PDF report
      pdfBlob = await generateChildReport(childData, {
        includeCharts,
        includeTimeline
      });
    } else {
      // Screenshot method
      const element = document.getElementById(elementId);
      if (!element) {
        throw new Error('Dashboard element not found');
      }
      
      pdfBlob = await htmlToPDF(element, {
        filename,
        quality: 0.95,
        scale: 1.5
      });
    }
    
    // Download the PDF
    const success = downloadPDF(pdfBlob, filename);
    
    if (!success) {
      throw new Error('فشل في تحميل الملف');
    }
    
    return {
      success: true,
      filename,
      size: pdfBlob.size
    };
    
  } catch (error) {
    console.error('Dashboard export failed:', error);
    throw error;
  }
};

export default {
  htmlToPDF,
  generateChildReport,
  downloadPDF,
  previewPDF,
  exportDashboardPDF
}; 