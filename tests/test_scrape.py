import pandas as pd
import pytest

import logger
import scrape

PAGE = """
<html><body>
<div class="a-section imdb-scroll-table mojo-gutter">
  <table>
    <tr><th>Rank</th><th>Release Group</th><th>Worldwide</th></tr>
    <tr><td>1</td><td><a href="#">Bad Boys for Life</a></td><td>$419,074,646</td></tr>
    <tr><td>2</td><td>Sonic the Hedgehog</td><td>$306,766,470</td></tr>
  </table>
</div>
</body></html>
"""


def test_parse_table():
    df = scrape.parse_table(PAGE)
    assert list(df.columns) == ["Rank", "Release Group", "Worldwide"]
    assert df.iloc[0].tolist() == ["1", "Bad Boys for Life", "$419,074,646"]
    assert len(df) == 2


def test_parse_table_missing():
    assert scrape.parse_table("<html><body>nothing</body></html>") is None


def test_run_writes_csv_per_year(tmp_path, monkeypatch):
    monkeypatch.setattr(scrape, "DATA_DIR", str(tmp_path))
    fetched = []

    def fake_fetch(url):
        fetched.append(url)
        return None if "2018" in url else PAGE

    monkeypatch.setattr(scrape, "url_to_txt", fake_fetch)

    result = scrape.run(start_year=2020, years_ago=2)

    assert result == {"finished": [2020, 2019], "failed": [2018]}
    assert fetched[0] == "https://www.boxofficemojo.com/year/world/2020/"
    assert pd.read_csv(tmp_path / "2020.csv")["Release Group"].tolist() == [
        "Bad Boys for Life",
        "Sonic the Hedgehog",
    ]
    assert not (tmp_path / "2018.csv").exists()


@pytest.mark.parametrize("year,back", [(20, 0), (2020, -1), ("2020", 0)])
def test_run_validates_input(year, back):
    with pytest.raises(ValueError):
        scrape.run(start_year=year, years_ago=back)


def test_trigger_log_save(tmp_path, monkeypatch):
    monkeypatch.setattr(logger, "log_dir", str(tmp_path))
    path = logger.trigger_log_save()
    assert ":" not in path.rsplit("/", 1)[-1]
    assert open(path).read().startswith("Scrape triggered at")
