"""
Handles /help, /status, and /tip commands.
"""

import logging
import random

from telegram import Update
from telegram.ext import CommandHandler

from database.mongo import MongoClient

logger = logging.getLogger(__name__)

firestore = MongoClient()
RAZORPAY_PRO_LINK = "https://razorpay.com/your-plan-link"

TIPS = [
    {"en": "Never share your UPI PIN with anyone, even if they claim to be from bank support.", "hi": "UPI PIN कभी किसी को न बताएं, भले ही वह बैंक सपोर्ट से होने का दावा करे।"},
    {"en": "Collect requests can debit money FROM your account. Only approve requests you initiated.", "hi": "Collect request आपके खाते से पैसे निकाल सकती है। केवल वही requests approve करें जो आपने खुद भेजी हों।"},
    {"en": "KYC expiry messages with links are almost always scams. Always use the official app or visit the bank.", "hi": "KYC एक्सपायरी के संदेशों में दिए गए लिंक लगभग हमेशा scam होते हैं। हमेशा ऑफिशियल ऐप या बैंक जाएं।"},
    {"en": "QR codes should never have pre-filled amounts. Always scan and then enter the amount yourself.", "hi": "QR कोड में पहले से भरी हुई राशि नहीं होनी चाहिए। हमेशा स्कैन करें और फिर खुद राशि डालें।"},
    {"en": "Lottery winnings never require a processing fee. If they ask for money first, it's a scam.", "hi": "लॉटरी जीतने पर कभी प्रोसेसिंग फीस नहीं लगती। अगर पहले पैसे मांगे, तो यह scam है।"},
    {"en": "Never share OTP with anyone. Banks and payment apps never ask for OTP over call.", "hi": "OTP कभी किसी को न दें। बैंक और पेमेंट ऐप कभी फोन पर OTP नहीं मांगते।"},
    {"en": "SIM swap scam: If your phone loses network suddenly, call your operator immediately.", "hi": "SIM swap scam: अगर आपका फोन अचानक नेटवर्क खो दे, तो तुरंत अपने ऑपरेटर को कॉल करें।"},
    {"en": "Fake customer care numbers on Google search are common. Always use the number from the official app.", "hi": "Google सर्च पर नकली कस्टमर केयर नंबर आम हैं। हमेशा ऑफिशियल ऐप से नंबर लें।"},
    {"en": "If a QR code looks tampered or pasted over another QR, don't scan it.", "hi": "अगर QR कोड छेड़छाड़ किया हुआ लगे या दूसरे QR के ऊपर चिपका हो, तो स्कैन न करें।"},
    {"en": "Screen sharing apps give scammers full access to your phone. Never install AnyDesk/TeamViewer for support.", "hi": "स्क्रीन शेयरिंग ऐप से scammers को आपके फोन की पूरी पहुंच मिल जाती है। सपोर्ट के लिए AnyDesk/TeamViewer कभी इंस्टॉल न करें।"},
    {"en": "UPI ID like 'paytm@paytm' or 'gpay@okhdfcbank' are legitimate. Check for slight misspellings on fake IDs.", "hi": "असली UPI ID जैसे 'paytm@paytm' होते हैं। नकली IDs में हल्की स्पेलिंग गलती देखें।"},
    {"en": "Social media job offers with high pay and no interview are red flags.", "hi": "सोशल मीडिया पर बिना इंटरव्यू के हाई पे वाली नौकरी के ऑफर लाल झंडे हैं।"},
    {"en": "If someone sends you a check and asks you to send money back, it's a fake check scam.", "hi": "अगर कोई आपको चेक भेजकर वापस पैसे भेजने को कहे, तो यह fake check scam है।"},
    {"en": "Payment received notifications with 'check full details' links are phishing.", "hi": "'पूरी जानकारी जांचें' लिंक वाले पेमेंट रिसीव्ड नोटिफिकेशन फिशिंग होते हैं।"},
    {"en": "Free Wi-Fi networks at public places can steal your UPI credentials. Use mobile data for transactions.", "hi": "सार्वजनिक स्थानों पर फ्री Wi-Fi आपके UPI क्रेडेंशियल चुरा सकते हैं। लेन-देन के लिए मोबाइल डेटा का उपयोग करें।"},
    {"en": "Enable two-factor authentication on your UPI apps for extra security.", "hi": "अतिरिक्त सुरक्षा के लिए अपने UPI ऐप पर टू-फैक्टर ऑथेंटिकेशन चालू करें।"},
    {"en": "Never respond to calls asking for your ATM card number or CVV.", "hi": "अपने ATM कार्ड नंबर या CVV मांगने वाले कॉल का कभी जवाब न दें।"},
    {"en": "Fraudsters use deepfake voice tech to mimic family members. Verify with a video call.", "hi": "ठग परिवार के सदस्यों की आवाज़ नकल करने के लिए डीपफेक तकनीक का उपयोग करते हैं। वीडियो कॉल से पुष्टि करें।"},
    {"en": "Vishing (voice phishing) scammers pretend to be bank officials. Never share personal details on call.", "hi": "विशिंग (वॉइस फिशिंग) में ठग बैंक अधिकारी बनते हैं। फोन पर कभी व्यक्तिगत जानकारी न दें।"},
    {"en": "If a friend sends you a UPI collect request from a different number, call them to confirm.", "hi": "अगर कोई दोस्त अलग नंबर से UPI collect request भेजे, तो फोन करके पुष्टि करें।"},
    {"en": "Delete unused UPI IDs from your app to reduce attack surface.", "hi": "हमले की संभावना कम करने के लिए अपने ऐप से अनुपयोगी UPI ID हटाएं।"},
    {"en": "Set daily UPI transaction limits to minimize potential loss.", "hi": "संभावित नुकसान कम करने के लिए दैनिक UPI लेन-देन सीमा निर्धारित करें।"},
    {"en": "Report phishing SMS to 1908 (DoT's cyber cell).", "hi": "फिशिंग SMS की शिकायत 1908 (DoT के साइबर सेल) पर करें।"},
    {"en": "Fake shopping sites with heavy discounts are common during festive seasons. Verify before paying.", "hi": "त्योहारी सीज़न में भारी छूट वाली नकली शॉपिंग साइट्स आम हैं। भुगतान से पहले सत्यापित करें।"},
    {"en": "Don't save UPI PIN in your phone's notes or contacts.", "hi": "UPI PIN को फ़ोन के नोट्स या कॉन्टैक्ट्स में सेव न करें।"},
    {"en": "Check transaction notification immediately after each UPI payment.", "hi": "प्रत्येक UPI भुगतान के तुरंत बाद लेन-देन की सूचना जांचें।"},
    {"en": "Beware of 'accidental' money transfers asking you to return the amount — it may be from a stolen account.", "hi": "'गलती से' पैसे ट्रांसफर करके वापस मांगने से सावधान — यह चोरी के खाते से हो सकता है।"},
    {"en": "Job scams: Real companies never ask for money for training or background checks.", "hi": "असली कंपनियां ट्रेनिंग या बैकग्राउंड चेक के लिए पैसे नहीं मांगतीं।"},
    {"en": "Romance scams: If someone you met online asks for money urgently, they're likely a fraudster.", "hi": "अगर ऑनलाइन मिला कोई व्यक्ति तुरंत पैसे मांगे, तो वह संभवतः धोखेबाज है।"},
    {"en": "Fake QR codes at parking lots and toll booths are on the rise. Check before scanning.", "hi": "पार्किंग और टोल बूथ पर नकली QR कोड बढ़ रहे हैं। स्कैन करने से पहले जांचें।"},
    {"en": "Never install apps from unknown APK links sent via WhatsApp.", "hi": "WhatsApp के माध्यम से भेजे गए अज्ञात APK लिंक से कभी ऐप इंस्टॉल न करें।"},
    {"en": "Cybercriminals create fake apps that look like genuine UPI apps. Only download from official stores.", "hi": "साइबर अपराधी असली UPI ऐप जैसे दिखने वाले नकली ऐप बनाते हैं। केवल आधिकारिक स्टोर से ही डाउनलोड करें।"},
    {"en": "Check your bank statement monthly for unauthorized transactions.", "hi": "अनधिकृत लेन-देन के लिए मासिक बैंक स्टेटमेंट जांचें।"},
    {"en": "Use a separate bank account for UPI with limited balance for daily use.", "hi": "दैनिक उपयोग के लिए सीमित बैलेंस वाला UPI के लिए अलग बैंक खाता उपयोग करें।"},
    {"en": "Block and report UPI scam numbers on the Chakshu portal (DoT).", "hi": "UPI scam नंबरों को Chakshu पोर्टल (DoT) पर ब्लॉक और रिपोर्ट करें।"},
    {"en": "Don't click on 'Your parcel couldn't be delivered' links — they're phishing.", "hi": "'आपका पार्सल डिलीवर नहीं हो सका' लिंक पर क्लिक न करें — वे फिशिंग हैं।"},
    {"en": "Courier scams: You get a call about an illegal parcel in your name. Government agencies don't call for this.", "hi": "कूरियर स्कैम: आपको आपके नाम पर अवैध पार्सल के बारे में कॉल आती है। सरकारी एजेंसियां इसके लिए कॉल नहीं करतीं।"},
    {"en": "Keep your UPI apps updated to the latest version for security patches.", "hi": "सुरक्षा पैच के लिए अपने UPI ऐप को नवीनतम संस्करण में अपडेट रखें।"},
    {"en": "If a call claims your account will be frozen, hang up and call your bank directly.", "hi": "अगर कोई कॉल दावा करे कि आपका खाता फ्रीज़ हो जाएगा, तो फोन काट दें और सीधे अपने बैंक को कॉल करें।"},
    {"en": "Google Pay, PhonePe, Paytm will never call you. Anyone claiming to be from them is a scammer.", "hi": "Google Pay, PhonePe, Paytm आपको कभी कॉल नहीं करते। कोई भी उनसे होने का दावा करने वाला ठग है।"},
    {"en": "Fake investment schemes promising 10x returns are always scams.", "hi": "10x रिटर्न का वादा करने वाली नकली निवेश योजनाएं हमेशा scam होती हैं।"},
    {"en": "Never let anyone access your phone via remote apps like AnyDesk, TeamViewer, or QuickSupport.", "hi": "AnyDesk, TeamViewer या QuickSupport जैसे रिमोट ऐप के माध्यम से किसी को अपने फ़ोन तक पहुंच न दें।"},
    {"en": "Fake toll collection messages (FASTag) with payment links are common. Verify on the official app.", "hi": "भुगतान लिंक वाले नकली टोल संग्रह संदेश (FASTag) आम हैं। आधिकारिक ऐप पर सत्यापित करें।"},
    {"en": "Electricity bill payment scams: Fake messages with links to 'disconnect' are phishing.", "hi": "बिजली बिल भुगतान स्कैम: 'डिस्कनेक्ट' करने के लिंक वाले नकली संदेश फिशिंग हैं।"},
    {"en": "Fake income tax refund messages with links are a common phishing tactic.", "hi": "लिंक वाले नकली आयकर रिफंड संदेश एक सामान्य फिशिंग रणनीति है।"},
    {"en": "Your biometric data (fingerprint, face) is as sensitive as your PIN. Don't share it.", "hi": "आपका बायोमेट्रिक डेटा (फिंगरप्रिंट, चेहरा) आपके PIN जितना ही संवेदनशील है। इसे साझा न करें।"},
    {"en": "Fake loan approval messages asking for processing fee upfront are always scams.", "hi": "पहले प्रोसेसिंग फीस मांगने वाले नकली लोन मंजूरी संदेश हमेशा scam होते हैं।"},
    {"en": "Beware of sextortion emails claiming to have your webcam footage. They're mass bluffs.", "hi": "आपके वेबकैम फुटेज होने का दावा करने वाले सेक्सटॉरशन ईमेल से सावधान रहें। ये ब्लफ़ होते हैं।"},
    {"en": "If a buyer on OLX/Facebook asks for an advance payment, it's likely a scam.", "hi": "OLX/Facebook पर कोई खरीदार अग्रिम भुगतान मांगे, तो यह संभवतः scam है।"},
    {"en": "Booking scams: Fake hotel/rental listings with too-good-to-be-true prices.", "hi": "बुकिंग स्कैम: बहुत अच्छी कीमतों वाली नकली होटल/किराया सूची।"},
    {"en": "Use virtual card numbers for online shopping instead of your actual debit card.", "hi": "अपने वास्तविक डेबिट कार्ड के बजाय ऑनलाइन शॉपिंग के लिए वर्चुअल कार्ड नंबर का उपयोग करें।"},
    {"en": "Report cybercrime at cybercrime.gov.in within 24 hours of the incident.", "hi": "घटना के 24 घंटे के भीतर cybercrime.gov.in पर साइबर अपराध की रिपोर्ट करें।"},
    {"en": "Helpline 1930 — Call immediately if you lose money to a UPI fraud.", "hi": "हेल्पलाइन 1930 — अगर आप UPI धोखाधड़ी में पैसे खोते हैं तो तुरंत कॉल करें।"},
    {"en": "Fake KYC links may look like 'www.hdfc-bank.com' but real bank URLs don't have hyphens.", "hi": "नकली KYC लिंक 'www.hdfc-bank.com' जैसे दिख सकते हैं लेकिन असली बैंक URL में हाइफ़न नहीं होते।"},
    {"en": "Social media quizzes asking your pet's name, mother's maiden name are mining security answers.", "hi": "आपके पालतू जानवर का नाम, माता का पहला नाम पूछने वाले सोशल मीडिया क्विज़ सुरक्षा उत्तर चुरा रहे हैं।"},
    {"en": "Beware of fake charity appeals after natural disasters. Verify before donating.", "hi": "प्राकृतिक आपदाओं के बाद नकली चैरिटी अपील से सावधान रहें। दान करने से पहले सत्यापित करें।"},
    {"en": "Fraudsters use your personal info from data leaks to make scams convincing.", "hi": "ठग आपकी व्यक्तिगत जानकारी का उपयोग डेटा लीक से scam को विश्वसनीय बनाने के लिए करते हैं।"},
    {"en": "Never scan a QR code that someone shows you on their phone screen — it could be a payment QR.", "hi": "कभी भी किसी के फ़ोन स्क्रीन पर दिखाए गए QR कोड को स्कैन न करें — यह भुगतान QR हो सकता है।"},
    {"en": "If an online seller insists on UPI payment and avoids payment gateways, be suspicious.", "hi": "अगर कोई ऑनलाइन विक्रेता UPI भुगतान पर जोर देता है और पेमेंट गेटवे से बचता है, तो संदिग्ध रहें।"},
    {"en": "Keep a separate device or a secure folder for all your banking apps.", "hi": "अपने सभी बैंकिंग ऐप के लिए एक अलग डिवाइस या सुरक्षित फ़ोल्डर रखें।"},
]


async def help_handler(update: Update, context):
    msg = (
        "🛡️ FraudShield — Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "/check\n"
        "Screenshot ya UPI ID analyse karo\n"
        "Analyse any screenshot or UPI ID\n\n"
        "/lookup <UPI ID ya phone>\n"
        "Fraud database mein search karo\n"
        "Search our fraud database\n\n"
        "/report <UPI ID ya phone>\n"
        "Scammer ko report karo\n"
        "Report a scammer to our community\n\n"
        "/status\n"
        "Apna account dekho\n"
        "View your account and points\n\n"
        "/tip\n"
        "Random fraud awareness tip\n"
        "Get a fraud safety tip\n\n"
        "/help\n"
        "Yeh message dobara dekho\n"
        "Show this message again\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Koi bhi suspicious cheez mili? Turant /check karo! 🚀"
    )
    await update.message.reply_text(msg)


async def status_handler(update: Update, context):
    user_id = str(update.effective_user.id)
    user = await firestore.get_user(user_id)

    if not user:
        await update.message.reply_text(
            "Aap register nahi hain. /start se shuru karein."
        )
        return

    name = user.get("name", "User")
    city = user.get("city", "Unknown")
    risk_profile = user.get("risk_profile", "novice")
    plan = user.get("plan", "free")
    used = user.get("checks_used", 0)
    limit = user.get("checks_limit", 5)
    points = user.get("guardian_points", 0)
    badges = user.get("badges", [])
    freq = user.get("alert_frequency", "instant")

    badge_str = ", ".join(badges) if badges else "None yet — /report karo!"

    msg = (
        f"👤 {name}\n"
        f"📍 {city}\n"
        f"🎯 Risk Profile: {risk_profile}\n"
        "━━━━━━━━━━━\n"
        f"📊 Plan: {plan}\n"
        f"🔍 Checks: {used}/{limit} this month\n"
        f"⭐ Guardian Points: {points}\n"
        f"🏅 Badges: {badge_str}\n"
        f"🔔 Alerts: {freq}\n"
        "━━━━━━━━━━━\n"
    )

    if plan == "free":
        msg += (
            "\n⚠️ Free plan hai. Limited checks.\n"
            "Pro plan ₹49/month — unlimited checks, "
            "priority alerts, aur premium support.\n"
            f"Upgrade: {RAZORPAY_PRO_LINK}"
        )

    await update.message.reply_text(msg)


async def tip_handler(update: Update, context):
    tip = random.choice(TIPS)
    msg = (
        "💡 FraudShield Tip\n"
        "━━━━━━━━━━━━━━━━\n\n"
        f"{tip['en']}\n\n"
        f"🇮🇳 {tip['hi']}\n\n"
        "Safe rahein, alert rahein! 🛡️\n"
        "/tip ke liye phir se dabayein"
    )
    await update.message.reply_text(msg)


help_cmd_handler = CommandHandler("help", help_handler)
status_cmd_handler = CommandHandler("status", status_handler)
tip_cmd_handler = CommandHandler("tip", tip_handler)
