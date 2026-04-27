import os, smtplib, requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from anthropic import Anthropic
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

#client = Anthropic()

# ── CONFIG: Customize your categories & keywords here ──────
NEWS_CATEGORIES = ["technology", "sports", "business", "health", "science", "entertainment", "general"]
NEWS_KEYWORDS   = ["finance", "stock market", "crypto", "artificial intelligence", "startups"]
ARTICLES_PER_TOPIC = 3
# ───────────────────────────────────────────────────────────


# ── 1a. Fetch by Category (NewsAPI top-headlines) ──────────
def fetch_news_by_category(categories):
    api_key = os.getenv("NEWS_API_KEY")
    all_articles = []

    for category in categories:
        url = (
            f"https://newsapi.org/v2/top-headlines"
            f"?category={category}&pageSize={ARTICLES_PER_TOPIC}&language=en&apiKey={api_key}"
        )
        res = requests.get(url).json()
        articles = res.get("articles", [])
        all_articles.append({
            "topic": f"🗂 {category.upper()}",
            "articles": [
                {"title": a["title"], "description": a["description"], "url": a["url"]}
                for a in articles if a["title"]
            ]
        })
    return all_articles


# ── 1b. Fetch by Keyword (NewsAPI everything) ──────────────
def fetch_news_by_keyword(keywords):
    api_key = os.getenv("NEWS_API_KEY")
    all_articles = []

    for keyword in keywords:
        url = (
            f"https://newsapi.org/v2/everything"
            f"?q={keyword}&pageSize={ARTICLES_PER_TOPIC}&language=en"
            f"&sortBy=publishedAt&apiKey={api_key}"
        )
        res = requests.get(url).json()
        articles = res.get("articles", [])
        all_articles.append({
            "topic": f"🔍 {keyword.upper()}",
            "articles": [
                {"title": a["title"], "description": a["description"], "url": a["url"]}
                for a in articles if a["title"]
            ]
        })
    return all_articles


# ── 2. Summarize with GEMINI ───────────────────────────────


# Configure Gemini (add this near the top of your file, after load_dotenv())
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_news(news_data):
    news_text = ""
    for section in news_data:
        news_text += f"\n### {section['topic']}\n"
        for a in section["articles"]:
            news_text += f"- {a['title']}: {a['description']}\n  URL: {a['url']}\n"

    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",   # or "gemini-1.5-pro" for better quality
        generation_config={
            "max_output_tokens": 3000,
            "temperature": 0.7,
        }
    )

    prompt = f"""You are a news curator. Given the headlines below, create a 
clean, engaging daily news digest in HTML format. 

Rules:
- Group articles by their topic/category section
- Write 2-3 sentence summaries per article
- Add a brief "Why it matters" line per article
- Make article titles clickable links using the provided URLs
- Use clean styling with section headers, cards, and readable fonts
- Keep the tone professional but engaging

{news_text}

Return ONLY a valid HTML <div> block (not a full page). Include inline CSS for styling."""

    response = model.generate_content(prompt)

    # Strip markdown code fences if Gemini wraps response in ```html ... ```
    result = response.text.strip()
    if result.startswith("```"):
        result = result.split("```")[1]          # remove opening fence
        if result.startswith("html"):
            result = result[4:]                  # strip the "html" language tag
        result = result.rsplit("```", 1)[0]      # remove closing fence
    
    return result.strip()

# ── 3. Send Email ──────────────────────────────────────────
def send_email(html_content):
    sender    = os.getenv("EMAIL_SENDER")
    password  = os.getenv("EMAIL_APP_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    # Wrap digest in a full HTML email shell
    full_html = f"""
    <html><body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
      <div style="max-width: 700px; margin: auto; background: white; border-radius: 10px; 
                  padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h1 style="color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
          📰 Your Daily News Digest
        </h1>
        {html_content}
        <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; 
                  padding-top: 10px;">
          Delivered by your News Agent 🤖 | Categories: {', '.join(NEWS_CATEGORIES + NEWS_KEYWORDS)}
        </p>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Your Daily News Digest"
    msg["From"]    = sender
    msg["To"]      = recipient
    msg.attach(MIMEText(full_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, recipient, msg.as_string())
    print("✅ Email sent!")


# ── 4. Run Agent ───────────────────────────────────────────
if __name__ == "__main__":
    print("🔍 Fetching news by category...")
    category_news = fetch_news_by_category(NEWS_CATEGORIES)

    print("🔎 Fetching news by keyword...")
    keyword_news = fetch_news_by_keyword(NEWS_KEYWORDS)

    all_news = category_news + keyword_news

    print("🤖 Summarizing with Gemini...")
    digest = summarize_news(all_news)

    print("📧 Sending email...")
    send_email(digest)