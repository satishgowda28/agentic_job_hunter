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
            result = detect_ats(Portals(**data).companies)
            print(result)
        except yaml.YAMLError as err:
            print(err)


def detect_ats(portals: list[Portal]) -> dict:
    ats_keywords = ["greenhouse", "ashby", "lever"]
    result = {key: [] for key in ats_keywords}
    result["unmatched"] = []
    for portal in portals:
        url = portal.careers_url.lower()
        matched = False
        for key in ats_keywords:
            if key in url:
                result[key].append(portal)
                matched = True
                break
        if not matched:
            result["unmatched"].append(portal)
    return result


if __name__ == "__main__":
    scan_portals()
