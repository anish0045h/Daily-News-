"""
Test script to verify email SMTP authentication is working correctly.
Run this to test if your Gmail App Password is configured properly.
"""
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def test_email_auth():
    sender    = os.getenv("EMAIL_SENDER")
    password  = os.getenv("EMAIL_APP_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")
    
    print(f"📧 Testing email authentication...")
    print(f"   From: {sender}")
    print(f"   To:   {recipient}")
    
    # Check if credentials are set
    if not sender or not password or not recipient:
        print("❌ ERROR: Missing email credentials in .env file!")
        print("   Required: EMAIL_SENDER, EMAIL_APP_PASSWORD, EMAIL_RECIPIENT")
        return False
    
    # Create a simple test email
    msg = MIMEText("This is a test email to verify SMTP authentication is working correctly.", "plain")
    msg["Subject"] = "🧪 Email Authentication Test"
    msg["From"]    = sender
    msg["To"]      = recipient
    
    try:
        # Test SMTP connection and login
        print("🔗 Connecting to smtp.gmail.com:465...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            print("🔐 Attempting login...")
            smtp.login(sender, password)
            print("✅ Login successful!")
            
            print("📤 Sending test email...")
            smtp.sendmail(sender, recipient, msg.as_string())
            print("✅ Email sent successfully!")
            
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed! Error: {e}")
        print("   Make sure:")
        print("   1. EMAIL_SENDER is your Gmail address")
        print("   2. EMAIL_APP_PASSWORD is an App Password (not your regular password)")
        print("   3. 2-Factor Authentication is enabled on your Google account")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_email_auth()
    if success:
        print("\n✅ All tests passed! Email authentication is working correctly.")
    else:
        print("\n❌ Test failed. Check your credentials and try again.")