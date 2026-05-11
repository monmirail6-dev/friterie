import json
import os

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def get_next_id():
    users = load_users()
    liste_ids_normaux = []

    for id in users:
        if id != "2641987":
            liste_ids_normaux.append(int(id))

    if not liste_ids_normaux:
        return "0000001"

    next_id = max(liste_ids_normaux) + 1
    return str(next_id).zfill(7)

def create_user(name, password, admin=False):
    users = load_users()
    new_id = get_next_id()

    users[new_id] = {
        "name": name,
        "password": password,
        "admin": admin
    }

    save_users(users)
    return new_id

def authenticate(id, password):
    users = load_users()

    if id not in users:
        return False

    if users[id]["password"] != password:
        return False

    return True, users[id]["admin"]

def modify_user(id, new_name=None, new_password=None, new_admin=None):
    users = load_users()

    if id not in users:
        return False

    if id == "2641987":
        if new_admin is not None and new_admin is False:
            return False
        if new_name is not None and new_name != "Bobo":
            return False

    if new_name is not None:
        users[id]["name"] = new_name

    if new_password is not None:
        users[id]["password"] = new_password

    if new_admin is not None:
        users[id]["admin"] = new_admin

    save_users(users)
    return True

def delete_user(id):
    users = load_users()

    if id == "2641987":
        return False

    if id not in users:
        return False

    del users[id]
    save_users(users)
    return True

def change_password(id, old_password, new_password):
    users = load_users()

    if id not in users:
        return False

    if id == "2641987" and old_password != users[id]["password"]:
        return False

    if users[id]["password"] != old_password:
        return False

    users[id]["password"] = new_password
    save_users(users)
    return True

def users_list():
    return load_users()

def create_bobo_admin():
    users = load_users()

    if "2641987" not in users:
        users["2641987"] = {
            "name": "Bobo",
            "password": "Fl0t$T!s",
            "admin": True
        }
    else:
        users["2641987"]["admin"] = True
        users["2641987"]["name"] = "Bobo"

    save_users(users)
    return True
