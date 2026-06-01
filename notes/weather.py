try:
    import requests
except ImportError:
    print("Error: requests module is not installed. Install it with: pip install requests")
    exit(1)

def get_weather(city):
    # Validate input: ensure city is a string and not empty
    if not isinstance(city, str) or not city.strip():
        print(f"Error: Invalid city name '{city}' — must be a non-empty string")
        return
    
    # Sanitize: strip whitespace, no special characters that could break the URL
    city = city.strip()
    if not city.replace(" ", "").isalnum():
        print(f"Error: City name '{city}' contains invalid characters")
        return
    
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        current = data["current_condition"][0]
        temp_f = current["temp_F"]
        desc = current["weatherDesc"][0]["value"]
        
        print(f"{city}: {temp_f}°F — {desc}")
    
    except requests.exceptions.Timeout:
        print(f"Error: Request for '{city}' timed out")
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error for '{city}' — {e.response.status_code}")
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error: Invalid response data for '{city}' — {type(e).__name__}")
    except Exception as e:
        print(f"Error: Unexpected error for '{city}' — {type(e).__name__}")

def get_weather_for_cities(cities):
    if not isinstance(cities, list):
        print("Error: Input must be a list of cities")
        return
    
    for city in cities:
        get_weather(city)

get_weather_for_cities(["Kansas City", "New York", "Los Angeles"])