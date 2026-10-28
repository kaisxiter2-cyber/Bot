import os
import time
import requests
from bs4 import BeautifulSoup
import telebot
from playwright.sync_api import sync_playwright

TOKEN = "9148487888:AAFKUgA92tKKe05zV_j6rxkwtohCvfpfx8s"
bot = telebot.TeleBot(TOKEN)

TARGET_URL = "https://baccalaureate-educat-j5df.bolt.host/"

def fetch_free_proxy():
    """دالة لجلب فحص واختيار بروكسي حقيقي يعمل من الإنترنت"""
    try:
        response = requests.get("https://free-proxy-list.net/", timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_elements = soup.find('tbody').find_all('tr')
        
        for tr in tr_elements[:15]:
            tds = tr.find_all('td')
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            proxy_str = f"{ip}:{port}"
            if test_proxy(proxy_str):
                return proxy_str
    except Exception as e:
        print(f"Error fetching proxy: {e}")
    return None

def test_proxy(proxy):
    """التحقق من أن البروكسي يعمل قبل استخدامه"""
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        res = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=3)
        if res.status_code == 200:
            return True
    except:
        pass
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك! البوت جاهز بالكامل (مع دقة الشاشة، البروكسي، وتحميل الملفات). أرسل /run للبدء.")

@bot.message_handler(commands=['run'])
def run_automation(message):
    bot.reply_to(message, "🔍 جاري البحث عن بروكسي وتجهيز بيئة التشغيل...")
    
    working_proxy = fetch_free_proxy()
    proxy_arg = f"http://{working_proxy}" if working_proxy else None
    
    if working_proxy:
        bot.reply_to(message, f"✅ تم الاتصال عبر بروكسي: {working_proxy}")
    else:
        bot.reply_to(message, "⚠️ لم يتم العثور على بروكسي، سيتم المتابعة بالـ IP الأساسي...")

    try:
        with sync_playwright() as p:
            launch_args = {"headless": True}
            if proxy_arg:
                launch_args["proxy"] = {"server": proxy_arg}
                
            browser = p.chromium.launch(**launch_args)
            
            # 1. إعداد دقة الشاشة (Screen Resolution & Viewport) وبصمة جهاز حقيقي
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}, # دقة شاشة كاملة (Full HD)
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            bot.reply_to(message, "🌐 جاري الدخول إلى الموقع المستهدف بدقة شاشة 1920x1080...")
            page.goto(TARGET_URL)
            time.sleep(3)
            
            # 2. نظام التحميل الفعلي للملفات (File Downloads Engine)
            bot.reply_to(message, "📥 جاري البحث عن زر التحميل وبدء سحب الملف...")
            
            try:
                # ننتظر حدث التحميل عند الضغط على زر التحميل (يمكنك تعديل محدد الزر حسب تصميم موقعك مثل 'a.download', أو زر معين)
                # كمثال افتراضي نقوم بالانتظار وتفعيل حدث التحميل:
                with page.expect_download(timeout=15000) as download_info:
                    # اضغط هنا على زر التحميل في صفحتك (استبدل السlector بالزر الحقيقي لديك إن وجد، أو اضغط على أول زر تحميل)
                    # page.click("text=Download") أو page.click("#download-btn")
                    # كمثال تجريبي سنضغط على أي رابط تحميل أو زر متاح في الصفحة:
                    page.eval_on_selector("a", "el => el.click()") 
                
                download = download_info.value
                # حفظ الملف في مجلد مؤقت داخل السيرفر
                file_path = os.path.join("/tmp", download.suggested_filename)
                download.save_as(file_path)
                
                bot.reply_to(message, f"🎉 تم تحميل الملف بنجاح وحفظه باسم: {download.suggested_filename}")
                
            except Exception as dl_err:
                bot.reply_to(message, f"ℹ️ ملاحظة حول التحميل المباشر: {str(dl_err)}\nتم فتح الصفحة ودقة الشاشة بنجاح، جاري إتمام العملية.")

            browser.close()
            
        bot.reply_to(message, "🚀 اكتملت الدفعة بنجاح تام!")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء التشغيل: {str(e)}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
            
