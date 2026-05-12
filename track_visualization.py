import requests

# Fetch only the Qualifying sessions for the entire 2023 season
url = "https://api.openf1.org/v1/sessions?year=2023&session_name=Qualifying"
response = requests.get(url)
sessions_data = response.json()

# Use exact country names to avoid substring bugs (like 'spa' in 'spain')
target_countries = ['Italy', 'Belgium', 'Singapore', 'Japan']

print("--- Exact Keys for 2023 Qualifying Sessions ---\n")

for session in sessions_data:
    country = session.get('country_name', '')
    
    if country in target_countries:
        print(f"Target Found: {country.upper()}")
        print(f"  -> Official Circuit Name: {session.get('circuit_short_name')}")
        print(f"  -> Location: {session.get('location')}")
        print(f"  -> Meeting Key (Weekend ID): {session.get('meeting_key')}")
        print(f"  -> Session Key (Qualifying ID): {session.get('session_key')}")
        print("-" * 45)