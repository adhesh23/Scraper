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
from readability import Document

app = Flask(__name__)

def extract_article_content(html):
    try:
        doc = Document(html)
        title = doc.short_title()
        summary_html = doc.summary()

        # Clean the HTML to plain text
        soup = BeautifulSoup(summary_html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return {"title": title, "text": text}
    except Exception as e:
        return {"title": "Error", "text": f"Failed to extract content: {e}"}

def scrape_article(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle", timeout=15000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(5)  # Ensure lazy-loaded content is fully rendered

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
