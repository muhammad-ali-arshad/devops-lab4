import os
from html import escape

from flask import Flask, jsonify, request

from news_sources import source_for
from scraper import ScrapeError, fetch_first_article
from summarizer import summarize


registration = os.environ.get("REGISTRATION", "")
source = source_for(registration)
app = Flask(__name__)


@app.get("/")
def home():
    return (
        "<!doctype html><html><head><title>DevOps News Summary</title></head><body>"
        f"<h1>Registration Number: {escape(registration)}</h1>"
        f"<p>News source: {escape(source.name)}</p>"
        "<p>Use <code>/get?keyword=your+keyword</code> to get an article summary.</p>"
        "</body></html>"
    )


@app.get("/health")
def health():
    return jsonify(status="ok", registration=registration)


@app.get("/get")
def get_summary():
    keyword = request.args.get("keyword", "").strip()
    if not keyword or len(keyword) > 100:
        return jsonify(error="keyword must be 1 to 100 characters"), 400
    try:
        url, article = fetch_first_article(source, keyword)
    except ScrapeError as exc:
        return jsonify(error=str(exc), registration=registration, newssource=source.name, keyword=keyword), 502
    return jsonify(
        registration=registration,
        newssource=source.name,
        keyword=keyword,
        url=url,
        summary=summarize(article, keyword),
    )
