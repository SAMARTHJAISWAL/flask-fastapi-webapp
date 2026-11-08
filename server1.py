"""Flask version of the scraper service."""
from flask import Flask, jsonify, request

from logger import trigger_log_save
from scrape import run as scrape_runner

app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello, world. this is Flask"


@app.route("/abc", methods=["GET"])
def abc_view():
    return "Hello, world. this is abc"


@app.route("/box-office-mojo-scraper", methods=["POST"])
def box_office_scraper_view():
    """Scrape Box Office Mojo. Optional JSON body: {"start_year": 2020, "years_ago": 1}."""
    body = request.get_json(silent=True) or {}
    trigger_log_save()
    try:
        result = scrape_runner(start_year=body.get("start_year"), years_ago=body.get("years_ago", 0))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8888, debug=True)
