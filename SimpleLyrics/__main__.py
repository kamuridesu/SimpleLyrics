import sys
import pydoc
import json
import requests
from bs4 import BeautifulSoup


class Letras:
    def __init__(self):
        self.headers_ff_mac: dict = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.root_url: str = "https://www.letras.mus.br"
        self.search_api_root_url: str = "https://solr.sscdn.co/letras/m1/?callback=LetrasSug&q="

    def search(self, search_term: str) -> dict | None:
        full_url: str = self.search_api_root_url + search_term
        response: requests.Response = requests.get(full_url, headers=self.headers_ff_mac)
        if response.status_code == 200:
            raw_result: str = response.text
            clean_result: list[dict] = json.loads(raw_result.replace("LetrasSug(", "")[:-2])['response']['docs']
            if isinstance(clean_result, list):
                if len(clean_result) < 1:
                    print("Error: No results found!")
                    raise SystemExit(1)
                return clean_result[0]
            return clean_result
        return None
    
    def getLyrics(self, result: dict) -> str:
        if all([x in result.keys() for x in ['dns', 'url']]):
            response: requests.Response = requests.get(f"{self.root_url}/{result['dns']}/{result['url']}")
            if response.status_code == 200:
                html_base: str = response.text
                soup: BeautifulSoup = BeautifulSoup(html_base, "html.parser")
                all_text = []
                lyrics = soup.find("div", {"class": "cnt-letra"})
                for x in lyrics.findAll("p"):
                    all_text.append(x.get_text("\n"))
                return "\n".join(all_text)


def cli():
    letras: Letras = Letras()
    result: dict | None = letras.search(' '.join(sys.argv[1:]))
    if result is not None:
        pydoc.pager(letras.getLyrics(result))


if __name__ == "__main__":
    cli()
