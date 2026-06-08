# Language system for GoalForge

LANGUAGES = {
    "fa": "🇮🇷 فارسی",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "ar": "🇸🇦 العربية",
    "de": "🇩🇪 Deutsch",
    "tr": "🇹🇷 Türkçe",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "hi": "🇮🇳 हिन्दी",
    "it": "🇮🇹 Italiano",
    "pt": "🇵🇹 Português",
}

TEXTS = {
    "welcome": {
        "fa": "سلام {name}! 👋\n\nمن Forge هستم — کوچ اجرایی شخصی‌ات.\n\nبهم بگو روی چه هدفی کار می‌کنی؟",
        "en": "Hello {name}! 👋\n\nI'm Forge — your personal AI coach.\n\nWhat goal are you working on?",
        "ru": "Привет {name}! 👋\n\nЯ Forge — твой персональный коуч.\n\nНад какой целью ты работаешь?",
        "ar": "مرحباً {name}! 👋\n\nأنا Forge — مدربك الشخصي.\n\nما الهدف الذي تعمل عليه؟",
        "de": "Hallo {name}! 👋\n\nIch bin Forge — dein persönlicher Coach.\n\nWoran arbeitest du gerade?",
        "tr": "Merhaba {name}! 👋\n\nBen Forge — kişisel koçun.\n\nHangi hedef üzerinde çalışıyorsun?",
        "fr": "Bonjour {name}! 👋\n\nJe suis Forge — ton coach personnel.\n\nSur quel objectif travailles-tu?",
        "es": "¡Hola {name}! 👋\n\nSoy Forge — tu coach personal.\n\n¿En qué objetivo estás trabajando?",
        "zh": "你好 {name}! 👋\n\n我是Forge — 你的私人教练。\n\n你正在为什么目标努力？",
        "ja": "こんにちは {name}! 👋\n\n私はForge — あなたのパーソナルコーチです。\n\nどんな目標に取り組んでいますか？",
        "hi": "नमस्ते {name}! 👋\n\nमैं Forge हूं — आपका व्यक्तिगत कोच।\n\nआप किस लक्ष्य पर काम कर रहे हैं?",
        "it": "Ciao {name}! 👋\n\nSono Forge — il tuo coach personale.\n\nSu quale obiettivo stai lavorando?",
        "pt": "Olá {name}! 👋\n\nSou Forge — seu coach pessoal.\n\nEm qual objetivo você está trabalhando?",
    },
    "choose_language": {
        "fa": "زبان خودت رو انتخاب کن:",
        "en": "Choose your language:",
        "ru": "Выберите ваш язык:",
        "ar": "اختر لغتك:",
        "de": "Wähle deine Sprache:",
        "tr": "Dilini seç:",
        "fr": "Choisissez votre langue:",
        "es": "Elige tu idioma:",
        "zh": "选择您的语言：",
        "ja": "言語を選択してください：",
        "hi": "अपनी भाषा चुनें:",
        "it": "Scegli la tua lingua:",
        "pt": "Escolha seu idioma:",
    },
    "commands_title": {
        "fa": "📌 دستورات GoalForge:",
        "en": "📌 GoalForge Commands:",
        "ru": "📌 Команды GoalForge:",
        "ar": "📌 أوامر GoalForge:",
        "de": "📌 GoalForge Befehle:",
        "tr": "📌 GoalForge Komutları:",
        "fr": "📌 Commandes GoalForge:",
        "es": "📌 Comandos GoalForge:",
        "zh": "📌 GoalForge 命令:",
        "ja": "📌 GoalForgeコマンド:",
        "hi": "📌 GoalForge कमांड:",
        "it": "📌 Comandi GoalForge:",
        "pt": "📌 Comandos GoalForge:",
    },
    "commands_body": {
        "fa": (
            "\n🎯 *هدف‌ها*\n"
            "/goal — هدف جدید\n"
            "/goals — لیست هدف‌ها\n\n"
            "📊 *پیشرفت*\n"
            "/checkin — چک‌این روزانه\n"
            "/streak — وضعیت streak\n"
            "/xp — XP و Level\n"
            "/achievements — دستاوردها\n"
            "/trust — Trust Score\n"
            "/report — گزارش هفتگی\n\n"
            "⚙️ *تنظیمات*\n"
            "/profile — پروفایل من\n"
            "/style — سبک کوچینگ\n"
            "/reminder — یادآوری روزانه\n"
            "/language — تغییر زبان\n"
            "/premium — وضعیت Premium"
        ),
        "en": (
            "\n🎯 *Goals*\n"
            "/goal — New goal\n"
            "/goals — List goals\n\n"
            "📊 *Progress*\n"
            "/checkin — Daily checkin\n"
            "/streak — Streak status\n"
            "/xp — XP & Level\n"
            "/achievements — Achievements\n"
            "/trust — Trust Score\n"
            "/report — Weekly report\n\n"
            "⚙️ *Settings*\n"
            "/profile — My profile\n"
            "/style — Coaching style\n"
            "/reminder — Daily reminder\n"
            "/language — Change language\n"
            "/premium — Premium status"
        ),
        "ru": (
            "\n🎯 *Цели*\n"
            "/goal — Новая цель\n"
            "/goals — Список целей\n\n"
            "📊 *Прогресс*\n"
            "/checkin — Ежедневный чекин\n"
            "/streak — Статус серии\n"
            "/xp — XP и уровень\n"
            "/achievements — Достижения\n"
            "/trust — Доверие\n"
            "/report — Еженедельный отчет\n\n"
            "⚙️ *Настройки*\n"
            "/profile — Мой профиль\n"
            "/style — Стиль коучинга\n"
            "/reminder — Напоминание\n"
            "/language — Язык\n"
            "/premium — Премиум"
        ),
        "de": (
            "\n🎯 *Ziele*\n"
            "/goal — Neues Ziel\n"
            "/goals — Ziele auflisten\n\n"
            "📊 *Fortschritt*\n"
            "/checkin — Tägliches Checkin\n"
            "/streak — Streak Status\n"
            "/xp — XP & Level\n"
            "/achievements — Erfolge\n"
            "/trust — Vertrauenspunktzahl\n"
            "/report — Wochenbericht\n\n"
            "⚙️ *Einstellungen*\n"
            "/profile — Mein Profil\n"
            "/style — Coaching-Stil\n"
            "/reminder — Erinnerung\n"
            "/language — Sprache\n"
            "/premium — Premium"
        ),
    },
    "goal_prompt": {
        "fa": "🎯 هدف جدیدت رو بنویس:\n\nمثال: میخوام در ۳ ماه زبان انگلیسی یاد بگیرم",
        "en": "🎯 Write your new goal:\n\nExample: I want to learn Spanish in 3 months",
        "ru": "🎯 Напишите вашу новую цель:\n\nПример: Хочу научиться играть на гитаре за 3 месяца",
        "ar": "🎯 اكتب هدفك الجديد:\n\nمثال: أريد تعلم اللغة الإنجليزية في 3 أشهر",
        "de": "🎯 Schreibe dein neues Ziel:\n\nBeispiel: Ich möchte in 3 Monaten Spanisch lernen",
        "tr": "🎯 Yeni hedefini yaz:\n\nÖrnek: 3 ayda İngilizce öğrenmek istiyorum",
        "fr": "🎯 Écris ton nouvel objectif:\n\nExemple: Je veux apprendre l'espagnol en 3 mois",
        "es": "🎯 Escribe tu nuevo objetivo:\n\nEjemplo: Quiero aprender inglés en 3 meses",
        "zh": "🎯 写下你的新目标：\n\n示例：我想在3个月内学会英语",
        "ja": "🎯 新しい目標を書いてください：\n\n例：3ヶ月で英語を学びたい",
        "hi": "🎯 अपना नया लक्ष्य लिखें:\n\nउदाहरण: मैं 3 महीने में अंग्रेजी सीखना चाहता हूं",
        "it": "🎯 Scrivi il tuo nuovo obiettivo:\n\nEsempio: Voglio imparare lo spagnolo in 3 mesi",
        "pt": "🎯 Escreva seu novo objetivo:\n\nExemplo: Quero aprender inglês em 3 meses",
    },
    "goal_saved": {
        "fa": "✅ هدفت ثبت شد:\n«{goal}»\n\n🔥 Forge این هدف رو دنبال میکنه.\n⭐ +10 XP",
        "en": "✅ Goal saved:\n«{goal}»\n\n🔥 Forge will track this goal.\n⭐ +10 XP",
        "ru": "✅ Цель сохранена:\n«{goal}»\n\n🔥 Forge будет следить за этой целью.\n⭐ +10 XP",
        "ar": "✅ تم حفظ الهدف:\n«{goal}»\n\n🔥 سيتابع Forge هذا الهدف.\n⭐ +10 XP",
        "de": "✅ Ziel gespeichert:\n«{goal}»\n\n🔥 Forge wird dieses Ziel verfolgen.\n⭐ +10 XP",
        "tr": "✅ Hedef kaydedildi:\n«{goal}»\n\n🔥 Forge bu hedefi takip edecek.\n⭐ +10 XP",
        "fr": "✅ Objectif sauvegardé:\n«{goal}»\n\n🔥 Forge suivra cet objectif.\n⭐ +10 XP",
        "es": "✅ Objetivo guardado:\n«{goal}»\n\n🔥 Forge seguirá este objetivo.\n⭐ +10 XP",
        "zh": "✅ 目标已保存：\n「{goal}」\n\n🔥 Forge将跟踪此目标。\n⭐ +10 XP",
        "ja": "✅ 目標が保存されました：\n「{goal}」\n\n🔥 Forgeはこの目標を追跡します。\n⭐ +10 XP",
        "hi": "✅ लक्ष्य सहेजा गया:\n«{goal}»\n\n🔥 Forge इस लक्ष्य को ट्रैक करेगा।\n⭐ +10 XP",
        "it": "✅ Obiettivo salvato:\n«{goal}»\n\n🔥 Forge seguirà questo obiettivo.\n⭐ +10 XP",
        "pt": "✅ Objetivo salvo:\n«{goal}»\n\n🔥 Forge acompanhará este objetivo.\n⭐ +10 XP",
    },
    "checkin_prompt": {
        "fa": "✅ چک‌این روزانه\n\nامروز چیکار کردی؟ بنویس:",
        "en": "✅ Daily Checkin\n\nWhat did you do today? Write it:",
        "ru": "✅ Ежедневный чекин\n\nЧто ты сделал сегодня? Напиши:",
        "ar": "✅ تسجيل يومي\n\nماذا فعلت اليوم؟ اكتب:",
        "de": "✅ Tägliches Checkin\n\nWas hast du heute gemacht? Schreibe es:",
        "tr": "✅ Günlük Checkin\n\nBugün ne yaptın? Yaz:",
        "fr": "✅ Checkin quotidien\n\nQu'as-tu fait aujourd'hui? Écris:",
        "es": "✅ Checkin diario\n\n¿Qué hiciste hoy? Escríbelo:",
        "zh": "✅ 每日打卡\n\n你今天做了什么？写下来：",
        "ja": "✅ デイリーチェックイン\n\n今日は何をしましたか？書いてください：",
        "hi": "✅ दैनिक चेक-इन\n\nआज आपने क्या किया? लिखें:",
        "it": "✅ Checkin giornaliero\n\nCosa hai fatto oggi? Scrivi:",
        "pt": "✅ Checkin diário\n\nO que você fez hoje? Escreva:",
    },
    "reminder_prompt": {
        "fa": "⏰ چه ساعتی Forge بهت پیام بده؟\n\nفرمت: HH:MM\nمثال: 21:30",
        "en": "⏰ What time should Forge message you?\n\nFormat: HH:MM\nExample: 21:30",
        "ru": "⏰ В какое время Forge должен писать вам?\n\nФормат: HH:MM\nПример: 21:30",
        "ar": "⏰ في أي وقت يجب أن يرسل Forge رسالة؟\n\nالتنسيق: HH:MM\nمثال: 21:30",
        "de": "⏰ Wann soll Forge dir eine Nachricht schicken?\n\nFormat: HH:MM\nBeispiel: 21:30",
        "tr": "⏰ Forge sana ne zaman mesaj atsın?\n\nFormat: HH:MM\nÖrnek: 21:30",
        "fr": "⏰ À quelle heure Forge doit vous envoyer un message?\n\nFormat: HH:MM\nExemple: 21:30",
        "es": "⏰ ¿A qué hora debe Forge enviarte un mensaje?\n\nFormato: HH:MM\nEjemplo: 21:30",
        "zh": "⏰ Forge应该什么时候给你发消息？\n\n格式：HH:MM\n示例：21:30",
        "ja": "⏰ Forgeは何時にメッセージを送りますか？\n\nフォーマット：HH:MM\n例：21:30",
        "hi": "⏰ Forge आपको किस समय संदेश भेजे?\n\nफॉर्मेट: HH:MM\nउदाहरण: 21:30",
        "it": "⏰ A che ora Forge ti deve inviare un messaggio?\n\nFormato: HH:MM\nEsempio: 21:30",
        "pt": "⏰ Que horas o Forge deve te enviar uma mensagem?\n\nFormato: HH:MM\nExemplo: 21:30",
    },
    "style_prompt": {
        "fa": "سبک کوچینگ Forge رو انتخاب کن:",
        "en": "Choose Forge's coaching style:",
        "ru": "Выберите стиль коучинга Forge:",
        "ar": "اختر أسلوب التدريب الخاص بـ Forge:",
        "de": "Wähle Forges Coaching-Stil:",
        "tr": "Forge'un koçluk tarzını seç:",
        "fr": "Choisissez le style de coaching de Forge:",
        "es": "Elige el estilo de coaching de Forge:",
        "zh": "选择Forge的教练风格：",
        "ja": "Forgeのコーチングスタイルを選択してください：",
        "hi": "Forge की कोचिंग शैली चुनें:",
        "it": "Scegli lo stile di coaching di Forge:",
        "pt": "Escolha o estilo de coaching do Forge:",
    },
}

STYLE_BUTTONS = {
    "fa": ["😊 دوستانه", "💪 سخت‌گیر", "⚔️ نظامی", "🧠 مربی", "📊 حرفه‌ای"],
    "en": ["😊 Friendly", "💪 Strict", "⚔️ Military", "🧠 Mentor", "📊 Professional"],
    "ru": ["😊 Дружелюбный", "💪 Строгий", "⚔️ Военный", "🧠 Наставник", "📊 Профессиональный"],
    "ar": ["😊 ودي", "💪 صارم", "⚔️ عسكري", "🧠 مرشد", "📊 احترافي"],
    "de": ["😊 Freundlich", "💪 Streng", "⚔️ Militärisch", "🧠 Mentor", "📊 Professionell"],
    "tr": ["😊 Dostane", "💪 Sert", "⚔️ Askeri", "🧠 Mentor", "📊 Profesyonel"],
    "fr": ["😊 Amical", "💪 Strict", "⚔️ Militaire", "🧠 Mentor", "📊 Professionnel"],
    "es": ["😊 Amigable", "💪 Estricto", "⚔️ Militar", "🧠 Mentor", "📊 Profesional"],
    "zh": ["😊 友好", "💪 严格", "⚔️ 军事", "🧠 导师", "📊 专业"],
    "ja": ["😊 フレンドリー", "💪 厳格", "⚔️ 軍事", "🧠 メンター", "📊 プロフェッショナル"],
    "hi": ["😊 मित्रवत", "💪 सख्त", "⚔️ सैन्य", "🧠 मार्गदर्शक", "📊 पेशेवर"],
    "it": ["😊 Amichevole", "💪 Severo", "⚔️ Militare", "🧠 Mentore", "📊 Professionale"],
    "pt": ["😊 Amigável", "💪 Rigoroso", "⚔️ Militar", "🧠 Mentor", "📊 Profissional"],
}

STYLE_MAP = {btn: style for style, btn_list in {
    "friendly": ["😊 دوستانه","😊 Friendly","😊 Дружелюбный","😊 ودي","😊 Freundlich","😊 Dostane","😊 Amical","😊 Amigable","😊 友好","😊 フレンドリー","😊 मित्रवत","😊 Amichevole","😊 Amigável"],
    "strict": ["💪 سخت‌گیر","💪 Strict","💪 Строгий","💪 صارم","💪 Streng","💪 Sert","💪 Strict","💪 Estricto","💪 严格","💪 厳格","💪 सख्त","💪 Severo","💪 Rigoroso"],
    "military": ["⚔️ نظامی","⚔️ Military","⚔️ Военный","⚔️ عسكري","⚔️ Militärisch","⚔️ Askeri","⚔️ Militaire","⚔️ Militar","⚔️ 军事","⚔️ 軍事","⚔️ सैन्य","⚔️ Militare","⚔️ Militar"],
    "mentor": ["🧠 مربی","🧠 Mentor","🧠 Наставник","🧠 مرشد","🧠 Mentor","🧠 Mentor","🧠 Mentor","🧠 Mentor","🧠 导师","🧠 メンター","🧠 मार्गदर्शक","🧠 Mentore","🧠 Mentor"],
    "professional": ["📊 حرفه‌ای","📊 Professional","📊 Профессиональный","📊 احترافي","📊 Professionell","📊 Profesyonel","📊 Professionnel","📊 Profesional","📊 专业","📊 プロフェッショナル","📊 पेशेवर","📊 Professionale","📊 Profissional"],
}.items() for btn in btn_list}


def t(key, lang, **kwargs):
    """Get translated text"""
    texts = TEXTS.get(key, {})
    text = texts.get(lang) or texts.get("en", key)
    if kwargs:
        text = text.format(**kwargs)
    return text
