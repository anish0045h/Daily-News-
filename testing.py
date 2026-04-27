import os
from dotenv import load_dotenv
from google import genai

# 1. Force load the .env from the current directory
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

# --- DIAGNOSTIC CHECK ---
if api_key is None:
    print("❌ ERROR: Your .env file was NOT found or 'GEMINI_API_KEY' is empty.")
    print(f"Current Working Directory: {os.getcwd()}")
else:
    # Print only the first and last 4 chars for security
    print(f"✅ Key detected: {api_key[:4]}...{api_key[-4:]}")
    
    # 2. Try the connection with the 2026 SDK
    client = genai.Client(api_key=api_key)
    try:
        # gemini-3-flash-preview is the active 2026 free model
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents="Testing"
        )
        print("🚀 SUCCESS! The API key is valid and working.")
    except Exception as e:
        print(f"❌ API CALL FAILED: {e}")