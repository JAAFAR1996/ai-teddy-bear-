import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  ar: {
    translation: {
      common: {
        appName: 'دبدوب الذكي',
        welcome: 'مرحباً',
        loading: 'جاري التحميل...',
        error: 'حدث خطأ',
        retry: 'إعادة المحاولة',
        save: 'حفظ',
        cancel: 'إلغاء',
        delete: 'حذف',
        edit: 'تعديل',
        add: 'إضافة',
        search: 'بحث',
        filter: 'تصفية',
        export: 'تصدير',
        import: 'استيراد',
        logout: 'تسجيل الخروج',
        settings: 'الإعدادات',
        profile: 'الملف الشخصي',
        dashboard: 'لوحة التحكم',
        noData: 'لا توجد بيانات',
      },
      navigation: {
        dashboard: 'لوحة التحكم',
        conversations: 'المحادثات',
        childProfile: 'ملف الطفل',
        reports: 'التقارير',
        analytics: 'التحليلات',
        emergency: 'الطوارئ',
        settings: 'الإعدادات',
      },
      dashboard: {
        title: 'لوحة تحكم الوالدين',
        subtitle: 'تابع نشاط أطفالك مع الذكاء الاصطناعي',
        stats: {
          dailyConversations: 'المحادثات اليوم',
          emotionalState: 'الحالة العاطفية',
          activityTime: 'وقت النشاط',
          educationalProgress: 'التقدم التعليمي',
        },
        emotions: {
          happy: 'سعيد',
          sad: 'حزين',
          angry: 'غاضب',
          neutral: 'محايد',
          excited: 'متحمس',
          calm: 'هادئ',
        },
      },
      conversations: {
        title: 'المحادثات',
        subtitle: 'تتبع محادثات طفلك مع دبدوب الذكي',
        search: 'البحث في المحادثات...',
        filter: {
          all: 'الكل',
          today: 'اليوم',
          week: 'هذا الأسبوع',
          month: 'هذا الشهر',
        },
        empty: 'لا توجد محادثات',
        details: {
          transcript: 'نص المحادثة',
          emotions: 'المشاعر المكتشفة',
          duration: 'المدة',
          date: 'التاريخ',
        },
      },
      child: {
        title: 'ملف الطفل',
        info: {
          name: 'الاسم',
          age: 'العمر',
          gender: 'الجنس',
          interests: 'الاهتمامات',
          preferredLanguage: 'اللغة المفضلة',
        },
        stats: {
          totalConversations: 'إجمالي المحادثات',
          averageDuration: 'متوسط مدة المحادثة',
          favoriteTopics: 'المواضيع المفضلة',
          emotionalTrend: 'اتجاه المشاعر',
        },
      },
      reports: {
        title: 'التقارير',
        types: {
          daily: 'تقرير يومي',
          weekly: 'تقرير أسبوعي',
          monthly: 'تقرير شهري',
          custom: 'تقرير مخصص',
        },
        generate: 'إنشاء تقرير',
        download: 'تحميل PDF',
        email: 'إرسال بالبريد الإلكتروني',
      },
      emergency: {
        title: 'تنبيهات الطوارئ',
        subtitle: 'تنبيهات السلامة والمخاوف الفورية',
        types: {
          safety: 'مخاوف السلامة',
          behavioral: 'تغيرات سلوكية',
          emotional: 'ضائقة عاطفية',
          content: 'محتوى غير مناسب',
        },
        actions: {
          dismiss: 'تجاهل',
          investigate: 'تحقيق',
          contact: 'اتصال',
        },
      },
      auth: {
        login: {
          title: 'تسجيل الدخول',
          email: 'البريد الإلكتروني',
          password: 'كلمة المرور',
          remember: 'تذكرني',
          forgot: 'هل نسيت كلمة المرور؟',
          submit: 'دخول',
          noAccount: 'ليس لديك حساب؟',
          signup: 'إنشاء حساب',
        },
        errors: {
          invalidCredentials: 'بيانات الدخول غير صحيحة',
          networkError: 'خطأ في الشبكة',
          serverError: 'خطأ في الخادم',
        },
      },
    },
  },
  en: {
    translation: {
      common: {
        appName: 'AI Teddy Bear',
        welcome: 'Welcome',
        loading: 'Loading...',
        error: 'An error occurred',
        retry: 'Retry',
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        add: 'Add',
        search: 'Search',
        filter: 'Filter',
        export: 'Export',
        import: 'Import',
        logout: 'Logout',
        settings: 'Settings',
        profile: 'Profile',
        dashboard: 'Dashboard',
        noData: 'No data available',
      },
      navigation: {
        dashboard: 'Dashboard',
        conversations: 'Conversations',
        childProfile: 'Child Profile',
        reports: 'Reports',
        analytics: 'Analytics',
        emergency: 'Emergency',
        settings: 'Settings',
      },
      dashboard: {
        title: 'Parent Dashboard',
        subtitle: 'Monitor your children\'s activity with AI',
        stats: {
          dailyConversations: 'Daily Conversations',
          emotionalState: 'Emotional State',
          activityTime: 'Activity Time',
          educationalProgress: 'Educational Progress',
        },
        emotions: {
          happy: 'Happy',
          sad: 'Sad',
          angry: 'Angry',
          neutral: 'Neutral',
          excited: 'Excited',
          calm: 'Calm',
        },
      },
      conversations: {
        title: 'Conversations',
        subtitle: 'Track your child\'s conversations with AI Teddy',
        search: 'Search conversations...',
        filter: {
          all: 'All',
          today: 'Today',
          week: 'This Week',
          month: 'This Month',
        },
        empty: 'No conversations found',
        details: {
          transcript: 'Transcript',
          emotions: 'Detected Emotions',
          duration: 'Duration',
          date: 'Date',
        },
      },
      child: {
        title: 'Child Profile',
        info: {
          name: 'Name',
          age: 'Age',
          gender: 'Gender',
          interests: 'Interests',
          preferredLanguage: 'Preferred Language',
        },
        stats: {
          totalConversations: 'Total Conversations',
          averageDuration: 'Average Duration',
          favoriteTopics: 'Favorite Topics',
          emotionalTrend: 'Emotional Trend',
        },
      },
      reports: {
        title: 'Reports',
        types: {
          daily: 'Daily Report',
          weekly: 'Weekly Report',
          monthly: 'Monthly Report',
          custom: 'Custom Report',
        },
        generate: 'Generate Report',
        download: 'Download PDF',
        email: 'Email Report',
      },
      emergency: {
        title: 'Emergency Alerts',
        subtitle: 'Safety alerts and immediate concerns',
        types: {
          safety: 'Safety Concern',
          behavioral: 'Behavioral Change',
          emotional: 'Emotional Distress',
          content: 'Inappropriate Content',
        },
        actions: {
          dismiss: 'Dismiss',
          investigate: 'Investigate',
          contact: 'Contact',
        },
      },
      auth: {
        login: {
          title: 'Login',
          email: 'Email',
          password: 'Password',
          remember: 'Remember me',
          forgot: 'Forgot password?',
          submit: 'Login',
          noAccount: 'Don\'t have an account?',
          signup: 'Sign up',
        },
        errors: {
          invalidCredentials: 'Invalid credentials',
          networkError: 'Network error',
          serverError: 'Server error',
        },
      },
    },
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'ar', // Default language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already does escaping
    },
    react: {
      useSuspense: false,
    },
  });

export default i18n; 