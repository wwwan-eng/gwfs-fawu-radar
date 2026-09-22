
import json, re, hashlib
from pathlib import Path
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://career.gdufs.edu.cn"
LIST = BASE + "/web/Index/jobs-brief-list"
OUT = Path("data/jobs.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; GDUFS-Fawu-Radar/1.0)"}

LEGAL_TERMS = [
    "法务", "法律", "法学", "法律事务", "法律顾问", "合规", "合规管理",
    "合同管理", "合同审核", "知识产权", "争议解决", "诉讼", "律师",
    "风控", "风险管理", "legal", "counsel", "compliance", "paralegal",
    "legal affairs", "legal counsel", "法务专员", "法务经理", "法务岗"
]

def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text

def classify(text):
    low = text.lower()
    hits = []
    for t in LEGAL_TERMS:
        if t.lower() in low and t not in hits:
            hits.append(t)
    # A single incidental "法律" in a disclaimer should not automatically become a hit.
    strong = {"法务","法律事务","法律顾问","合规","合同管理","合同审核","知识产权",
              "争议解决","诉讼","律师","legal","counsel","compliance","paralegal",
              "legal affairs","legal counsel","法务专员","法务经理","法务岗"}
    strong_hits = [x for x in hits if x in strong]
    score = min(100, len(strong_hits)*35 + len(hits)*8)
    return score >= 35, score, hits[:10]

def parse_detail(url):
    soup = BeautifulSoup(fetch(url), "html.parser")
    title = clean(soup.title.get_text(" ", strip=True) if soup.title else "")
    # Main page text; site content is server-rendered.
    text = clean(soup.get_text(" ", strip=True))
    # Try to get a cleaner body by excluding nav/footer.
    for sel in ["script","style","nav","footer"]:
        for x in soup.select(sel):
            x.decompose()
    body = clean(soup.get_text(" ", strip=True))
    date_m = re.search(r"20\d{2}/\d{1,2}/\d{1,2}", body)
    date = date_m.group(0) if date_m else ""
    legal, score, hits = classify(body)
    return {"title": title.replace(" - 广东外语外贸大学就业信息网","").strip(),
            "date": date, "url": url, "legal": legal, "score": score,
            "hits": hits, "excerpt": body[:700]}

def main():
    soup = BeautifulSoup(fetch(LIST), "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "jobs-brief-detail" in href:
            url = urljoin(BASE, href)
            title = clean(a.get_text(" ", strip=True))
            if url not in {x[0] for x in links}:
                links.append((url, title))
    # Current page plus first few pages gives a rolling history.
    # The workflow runs frequently; newest 15 are enough for change detection.
    links = links[:15]

    old = {}
    if OUT.exists():
        try:
            old = {x["url"]: x for x in json.loads(OUT.read_text(encoding="utf-8")).get("jobs", [])}
        except Exception:
            old = {}

    jobs = []
    for url, title in links:
        try:
            item = parse_detail(url)
            if title and not item["title"]:
                item["title"] = title
            jobs.append(item)
        except Exception as e:
            jobs.append({"title": title, "date":"", "url":url, "legal":False,
                         "score":0, "hits":[], "excerpt":"抓取失败："+str(e)})

    # Keep prior records that may have fallen off the first page.
    seen = {x["url"] for x in jobs}
    for url, item in old.items():
        if url not in seen:
            jobs.append(item)

    jobs.sort(key=lambda x: (x.get("date",""), x.get("score",0)), reverse=True)
    result = {
        "source": LIST,
        "source_name": "广东外语外贸大学就业信息网｜招聘简讯",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(jobs),
        "legal_count": sum(1 for x in jobs if x.get("legal")),
        "jobs": jobs[:100]
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
