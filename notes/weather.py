try:
    import requests
except ImportError:
    print("Error: requests module is not installed. Install it with: pip install requests")
    exit(1)

def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    current = data["current_condition"][0]
    temp_f = current["temp_F"]
    desc = current["weatherDesc"][0]["value"]
    
    print(f"{city}: {temp_f}°F — {desc}")

get_weather("New York")