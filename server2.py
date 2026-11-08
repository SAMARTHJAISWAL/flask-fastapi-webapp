"""FastAPI version of the scraper service."""
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from logger import trigger_log_save
from scrape import run as scrape_runner

app = FastAPI(title="Box Office Mojo scraper")


class ScrapeRequest(BaseModel):
    start_year: Optional[int] = None
    years_ago: int = 0


class ScrapeResult(BaseModel):
    finished: List[int]
    failed: List[int]


@app.get("/")
def hello_world():
    return {"hello": "world"}


@app.get("/abc")
def abc_view():
    return {"data": [1, 2, 3]}


@app.post("/box-office-mojo-scraper", response_model=ScrapeResult)
def scrape_runner_view(body: Optional[ScrapeRequest] = None):
    """Scrape Box Office Mojo and save each year's table to data/<year>.csv."""
    body = body or ScrapeRequest()
    trigger_log_save()
    try:
        return scrape_runner(start_year=body.start_year, years_ago=body.years_ago)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8888)
