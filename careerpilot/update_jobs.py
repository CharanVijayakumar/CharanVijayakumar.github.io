"""Public job feed updater. Never processes CVs, notes, or credentials."""
import json, datetime, pathlib, urllib.request, re, hashlib
p=pathlib.Path(__file__).with_name("jobs.json")
try: old=json.loads(p.read_text(encoding="utf-8"))
except (OSError,ValueError): old={"jobs":[]}
existing={x["id"]:x for x in old.get("jobs",[]) if "id" in x}
endpoint="https://remotive.com/api/remote-jobs?limit=100"
req=urllib.request.Request(endpoint,headers={"User-Agent":"CareerPilotIreland/1.0"})
try:
    with urllib.request.urlopen(req,timeout=25) as response:
        data=json.load(response)
except Exception as exc:
    print("Source unavailable; preserving existing feed:",exc)
    raise SystemExit(0)
terms=re.compile(r"cyber|security analyst|soc analyst|java|c\+\+|software engineer|software developer|it support|helpdesk|network engineer|graduate|junior",re.I)
location=re.compile(r"ireland|europe|worldwide|anywhere|global|remote",re.I)
new=0
for j in data.get("jobs",[]):
    title=j.get("title","")
    loc=j.get("candidate_required_location","")
    url=j.get("url","")
    if not terms.search(title) or not location.search(loc) or not url.startswith("https://"): continue
    uid="remotive-"+str(j.get("id") or hashlib.sha256(url.encode()).hexdigest()[:16])
    record={"id":uid,"title":title,"company":j.get("company_name",""),"location":loc,"url":url,"summary":"Remote job lead; verify Ireland eligibility, experience requirements, and sponsorship."}
    if uid not in existing: new+=1
    existing[uid]=record
# Keep previously seen listings rather than deleting them; visibility does not prove current availability.
out={"updated":datetime.datetime.now(datetime.timezone.utc).isoformat(),"jobs":list(existing.values())[:500]}
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("New jobs:",new,"Total retained:",len(out["jobs"]))
