import requests

# URL of your Replit server
SERVER_URL = "https://fb4af26b-2c13-4572-9233-7fe3e9997ba6-00-2h1z2uim9qyfu.kirk.replit.dev"

# Room info to register
room_data = {
    "room": "CoolRoom123",
    "port": 9000
}

try:
    # Send POST request to /register
    response = requests.post(f"{SERVER_URL}/register", json=room_data)

    # Print response
    if response.status_code == 200:
        print("[✅] Registered successfully:")
        print(response.json())
    else:
        print(f"[❌] Failed to register. Status code: {response.status_code}")
        print(response.text)

except Exception as e:
    print("[💥] Error sending request:", e)
