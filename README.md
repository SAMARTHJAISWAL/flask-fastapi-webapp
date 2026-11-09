# Web App with Flask and FastAPI

[![tests](https://github.com/SAMARTHJAISWAL/flask-fastapi-webapp/actions/workflows/tests.yml/badge.svg)](https://github.com/SAMARTHJAISWAL/flask-fastapi-webapp/actions/workflows/tests.yml)

The same small web-scraping service written twice, once with **Flask** (`server1.py`) and once with **FastAPI** (`server2.py`). A `POST` to `/box-office-mojo-scraper` downloads the worldwide box office table for a year from [Box Office Mojo](https://www.boxofficemojo.com/year/world/) and saves it as `data/<year>.csv`.

## Features

- Two interchangeable servers exposing the same routes, for comparing the frameworks side by side.
- Scraper (`scrape.py`) built on Requests + BeautifulSoup, writing tables to CSV with pandas. It can scrape one year or a range of past years.
- Each scrape request writes a timestamped trigger file to `logs/`.
- `trigger.py` calls the scraper endpoint of a running server (local or behind a tunnel such as ngrok).
- FastAPI's interactive docs at `/docs`.
- `data/2020.csv` is a sample of the output.

## Tech stack

Python 3.10+, Flask 3, FastAPI, Uvicorn, Gunicorn (macOS/Linux), Requests, BeautifulSoup4, pandas, pytest.

## Setup

```bash
git clone https://github.com/SAMARTHJAISWAL/flask-fastapi-webapp.git
cd flask-fastapi-webapp
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

Both servers listen on port 8888.

| Server | macOS / Linux | Windows (PowerShell) |
|--------|---------------|----------------------|
| Flask | `./run1.sh` (Gunicorn) or `python server1.py` | `./run1.ps1` |
| FastAPI | `./run2.sh` or `python server2.py` | `./run2.ps1` |

Trigger a scrape:

```bash
# current year
curl -X POST http://127.0.0.1:8888/box-office-mojo-scraper

# 2021 and 2020
curl -X POST http://127.0.0.1:8888/box-office-mojo-scraper \
  -H "Content-Type: application/json" -d '{"start_year": 2021, "years_ago": 1}'

# or
python trigger.py http://127.0.0.1:8888
```

Response:

```json
{"finished": [2021, 2020], "failed": []}
```

You can also run the scraper without a server: `python scrape.py 2021 1`.

## API

Both servers expose the same routes.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Hello-world response |
| `GET` | `/abc` | Demo route |
| `POST` | `/box-office-mojo-scraper` | Scrape and save CSVs. Optional JSON body: `start_year` (4-digit int, default current year), `years_ago` (int >= 0, default 0). Returns `{"finished": [...], "failed": [...]}`; 400 on invalid input |

FastAPI docs: <http://127.0.0.1:8888/docs>

## Environment variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `SCRAPER_URL` | `trigger.py` | Base URL of the server to call if no argument is given (default `http://127.0.0.1:8888`) |

## Project structure

```
server1.py      # Flask app
server2.py      # FastAPI app
scrape.py       # Box Office Mojo scraper -> data/<year>.csv
logger.py       # writes a timestamped file to logs/ per trigger
trigger.py      # client that calls the scraper endpoint
run1.* / run2.* # start scripts (sh for macOS/Linux, ps1 for Windows)
data/           # scraped CSVs (2020.csv is a committed sample)
tests/          # pytest suite (no network)
```

## Tests

The tests use an inline HTML fixture and stub out the scraper, so they make no network requests.

```bash
pip install -r requirements-dev.txt
pytest
```

The scraper depends on Box Office Mojo's page markup (`.imdb-scroll-table table`). If the site changes, `parse_table` will return nothing and the year is reported under `failed`.

## Licence

[MIT](LICENSE) © 2024–2026 Samarth Jaiswal
