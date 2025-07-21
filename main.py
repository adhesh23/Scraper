# ---------------------------------------
# 🧩 Force Playwright install on Replit
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

app = Flask(__name__)

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

            title = page.title()
            content = page.inner_text("body")
            browser.close()

            return {"url": url, "title": title, "text": content}
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
