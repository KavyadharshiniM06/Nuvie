import requests

api_key = "5b3ac94c5cb2bc8b5e010970c6f4fb61"  # v3 API Key
request_token = "7312557f779c92e98f147514c5b206ceb8caede7"

url = f"https://api.themoviedb.org/3/authentication/session/new?api_key={api_key}"
payload = {
    "request_token": request_token
}

response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
print(response.json())
