import json

try:
    with open("users.json", "r") as f:
        users_list = json.load(f)

    # Convert list of {username, password} to dict username: password
    users_dict = {user["username"]: user["password"] for user in users_list}

    with open("users.json", "w") as f:
        json.dump(users_dict, f, indent=2)

    print("✅ Converted users.json from list to dict successfully!")

except Exception as e:
    print("❌ Error converting users.json:", e)
