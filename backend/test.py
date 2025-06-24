import requests

url = "https://api.themoviedb.org/3/search/movie"
params = {
    "api_key": "bec5b5a6bf336427cd5a0c3c97567bb5",
    "query": "La La Land",
    "year": "2016"
}
headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print("✅ Status Code:", response.status_code)
    print("🧾 Response:", response.json())
except Exception as e:
    print("❌ Exception:", e)
