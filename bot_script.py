# bot_script.py (VPS တွင် Session ထုတ်ယူရန် Final Code)
import asyncio
import os
import json
import nest_asyncio
from playwright_extra import async_playwright
from playwright_extra.plugins import stealth

# --- Configuration (သင့်ရဲ့ Credentials) ---
# NOTE: ဤနေရာတွင် သင့်ရဲ့ Google Skills Boost အီးမေးလ်နှင့် စကားဝှက်ကို ထည့်သွင်းပါ
YOUR_EMAIL = "your_skills_boost_email@example.com" 
YOUR_PASSWORD = "your_skills_boost_password" 
SESSION_FILE = "telegram_session.json" 
BASE_URL = "https://www.skills.google/"
DASHBOARD_PATH = "/my_learning_progress"

async def save_session(context):
    """Save the current storage state (cookies/local storage) to the session file."""
    # Session File ကို Save လုပ်ခြင်း
    await context.storage_state(path=SESSION_FILE)
    print(f"INFO: Successfully saved fresh session to {SESSION_FILE}")

async def login_and_get_session(page, email, password):
    """Attempts to log in using email/password (Headed Mode တွင် လူကိုယ်တိုင် ဝင်ရောက်ရန်)"""
    try:
        print("INFO: Browser Window ကို ဖွင့်ပါပြီ။ VNC Viewer မှ Login ဝင်ပေးပါ။")
        
        await page.goto(BASE_URL, wait_until='domcontentloaded') 
        
        # 'Sign in' ခလုတ်ကို ရှာပြီး နှိပ်ခြင်း
        await page.click("text=Sign in", timeout=10000) 
        
        # Login စာမျက်နှာကို စောင့်ခြင်း
        await page.wait_for_url("**/users/sign_in", timeout=15000)
        
        # Email နှင့် Password ဖြည့်ရန် ပုံစံကို နှိပ်ခြင်း
        await page.click("text=Use email and password", force=True) 
        
        # Credentials များကို ဖြည့်သွင်းခြင်း (လူကိုယ်တိုင် ပြန်ပြင်နိုင်ရန်အတွက် ဖြည့်သွင်းပေးသည်)
        await page.locator('input[name="user[email]"]').fill(email, force=True) 
        await page.locator('input[name="user[password]"]').fill(password, force=True) 
        
        # Sign in ခလုတ်ကို နှိပ်ခြင်း
        await page.click("button:has-text('Sign in')", force=True, timeout=10000) 
        
        # --- 🛑 VNC ဖြင့် လူကိုယ်တိုင် ဝင်ရောက်ရမည့် နေရာ ---
        # CAPTCHA ကို ဖြေရှင်းပြီး Dashboard ကို ရောက်သည်အထိ VNC ဖြင့် စောင့်ပေးရမည်။
        
        print("INFO: VNC Viewer တွင် Login ဝင်တာ အောင်မြင်ဖို့ စောင့်ဆိုင်းနေပါသည်။")
        
        # Dashboard ကို ရောက်သည်အထိ စောင့်ခြင်း (အောင်မြင်မှုကို စောင့်ခြင်း)
        await page.wait_for_url("**" + DASHBOARD_PATH + "**", timeout=60000) # 60 စက္ကန့် စောင့်ပေးသည်
        
        # Login success, Session ကို save လုပ်ပါ
        await save_session(page.context)
        return True
    
    except Exception as e:
        print(f"FATAL ERROR: Login အောင်မြင်မှု မရှိပါ။ VNC ဖြင့် စစ်ဆေးပါ။: {e}")
        return False

async def main_session_extractor():
    """Main function to launch browser in Headed Mode."""
    # headless=False ဖြင့် Browser Window ကို ဖွင့်ခြင်း
    async with async_playwright(plugins=[stealth]) as p:
        # NOTE: VPS မှာ Run နေသောကြောင့် Headless=False သည် VNC မှ မြင်ရသော Window ဖြစ်လာမည်
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        result = await login_and_get_session(page, YOUR_EMAIL, YOUR_PASSWORD)
        
        await browser.close()
        return result

# Script ကို Run ပါ
if __name__ == "__main__":
    nest_asyncio.apply()
    print("--- Session Extraction Started ---")
    asyncio.run(main_session_extractor())
    print("--- Session Extraction Finished ---")
