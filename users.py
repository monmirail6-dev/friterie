import json
import os
import base64
import requests
import streamlit as st

USERS_FILE = "users.json"
REPO = "monmirail6-dev/friterie"
FILE_PATH = "users.json"

# =========================
# LOAD
# =========================
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

users = load_users()

# =========================
# SAVE
# =========================
def save_users():

    # ✅ local
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    # ✅ GitHub
    try:
        token = st.secrets["GITHUB_TOKEN"]

        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

        headers = {"Authorization": f"token {token}"}

        r = requests.get(url, headers=headers)
        data = r.json()
        sha = data["sha"]

        content_encoded = base64.b64encode(
            json.dumps(users, indent=4, ensure_ascii=False).encode()
        ).decode()

        requests.put(url, headers=headers, json={
            "message": "Update users",
            "content": content_encoded,
            "sha": sha
        })

    except Exception as e:
        print("GitHub error users:", e)


# =========================
# CRUD
# =========================
def get_next_id():
    ids = [int(i) for i in users if i != "2641987"]

    if not ids:
        return "0000001"

    return str(max(ids) + 1).zfill(7)


def create_user(name, password, admin=False):

    # ✅ vérifier unicité du nom
    for u in users.values():
        if u["name"].lower() == name.lower():
            return None  # déjà existant

    new_id = get_next_id()

    users[new_id] = {
        "name": name,
        "password": password,
        "admin": admin
    }

    save_users()
    return new_id
``


def users_list():
    return users


def delete_user(uid):
    if uid == "2641987" or uid not in users:
        return False

    del users[uid]
    save_users()
    return True


def modify_user(uid, new_name=None, new_password=None):
    if uid not in users:
        return False

    if new_name:
        users[uid]["name"] = new_name

    if new_password:
        users[uid]["password"] = new_password

    save_users()
    return True


# =========================
# AUTH
# =========================
def authenticate(uid, password):
    if uid not in users:
        return False
    return users[uid]["password"] == password


def change_password(uid, old_password, new_password):
    if uid not in users:
        return False

    if users[uid]["password"] != old_password:
        return False

    users[uid]["password"] = new_password
    save_users()
    return True


def create_bobo_admin():
    if "2641987" not in users:
        users["2641987"] = {
            "name": "Bobo",
            "password": "Fl0t$T!s",
            "admin": True
        }
        save_users()
