from urllib.parse import urlparse

import yaml

from agents.types import Portal, Portals

API_URL = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
    "lever": "https://api.lever.co/v0/postings/{slug}",
}


def scan_portals():
    with open("config/portals.yml", "r") as file:
        try:
            data = yaml.safe_load(file)
            companines = Portals(**data).companies
            for company in companines:
                ats = detect_ats(company)
                if ats is None:
                    continue
                else:
                    fetch_data(ats, company)
        except yaml.YAMLError as err:
            print(err)


def detect_ats(portals: Portal) -> str | None:
    ats_keywords = ["greenhouse", "ashby", "lever"]
    for key in ats_keywords:
        if key in portals.careers_url:
            return key
    return None


def fetch_data(ats: str, portal: Portal):
    api_template = API_URL.get(ats, "")
    if api_template != "":
        slug = urlparse(portal.careers_url).path.strip("/")
        api_url = api_template.replace("{slug}", slug)
        # call api call
    pass


if __name__ == "__main__":
    scan_portals()
