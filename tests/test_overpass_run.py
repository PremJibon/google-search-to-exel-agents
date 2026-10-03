import requests

servers = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]

bbox = "23.7685,90.3963,23.8115,90.4279"
query = f"""[out:json][timeout:15];
(
  node["leisure"="fitness_centre"]({bbox});
  way["leisure"="fitness_centre"]({bbox});
  node["amenity"="gym"]({bbox});
  way["amenity"="gym"]({bbox});
);
out center tags 30;"""

for s in servers:
    try:
        t0 = requests.post(s, data={"data": query}, headers={"User-Agent": "LeadFinderFree/2.1"}, timeout=15)
        print(s, "Status:", t0.status_code, "Elements:", len(t0.json().get("elements", [])))
    except Exception as e:
        print(s, "Error:", type(e).__name__, e)
