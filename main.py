# ---------------------------------------
# 🧩 Force Playwright install on Replit/Render
# ---------------------------------------
import subprocess
import sys

try:
    from playwright.sync_api import sync_playwright
except:
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.run([sys.executable, "-m", "playwright", "install"])
    from playwright.sync_api import sync_playwright

# ---------------------------------------
# 🚀 Flask + Scraper Setup
# ---------------------------------------
from flask import Flask, request, render_template
import time
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_article_content(html):
    soup = BeautifulSoup(html, "html.parser")

    # Get the title from <title> tag
    title = soup.title.string.strip() if soup.title else "No Title Found"

    # Try to locate an <article> or similar content-heavy div
    article = soup.find("article")
    if not article:
        article = soup.find("div", class_=lambda c: c and ("article" in c or "content" in c))

    if article:
        paragraphs = article.find_all(["p", "h2", "h3", "li"])
        body = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
    else:
        body = "❌ Could not extract structured article content."

    return {"title": title, "text": body}

def scrape_article(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=10000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            html = page.content()
            browser.close()

            extracted = extract_article_content(html)
            return {"url": url, "title": extracted["title"], "text": extracted["text"]}
    except Exception as e:
        return {"url": url, "title": "Error", "text": str(e)}

@app.route("/", methods=["GET", "POST"])
def index():
    articles = []
    if request.method == "POST":
        url_input = request.form.get("urls")
        urls = [u.strip() for u in url_input.split(",") if u.strip()]
        for url in urls:
            result = scrape_article(url)
            articles.append(result)
    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
