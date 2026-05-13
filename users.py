import json
import os
import base64
import requests
import streamlit as st

USERS_FILE = "users.json"
REPO = "monmirail6-dev/friterie"
FILE_PATH = "users.json"


# ============================================================
# 🔹 LOAD (CACHÉ)
# ============================================================
@st.cache_data
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


# ============================================================
# 🔹 SAVE LOCAL (SANS GITHUB)
# ============================================================
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    # 🔥 IMPORTANT → on reset le cache
    load_users.clear()


# ============================================================
# 🔹 SYNC GITHUB (MANUEL)
# ============================================================
def sync_users_github():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {token}"}

        users = load_users()

        r = requests.get(url, headers=headers)
        data = r.json()
        sha = data["sha"]

        content_encoded = base64.b64encode(
            json.dumps(users, indent=4, ensure_ascii=False).encode()
        ).decode()

        requests.put(url, headers=headers, json={
            "message": "Update users.json via Streamlit",
            "content": content_encoded,
            "sha": sha
        })

        return True

    except Exception as e:
        print(e)
        return False


# ============================================================
# 🔹 ID
# ============================================================
def get_next_id():
    users = load_users()

    ids = [int(i) for i in users if i != "2641987"]

    if not ids:
        return "0000001"

    return str(max(ids) + 1).zfill(7)


# ============================================================
# 🔹 CRUD
# ============================================================
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


def users_list():
    return load_users()


def delete_user(id):
    users = load_users()

    if id == "2641987" or id not in users:
        return False

    del users[id]
    save_users(users)
    return True


def modify_user(id, new_name=None, new_password=None, new_admin=None):
    users = load_users()

    if id not in users:
        return False

    if id == "2641987":
        if new_admin is False:
            return False
        if new_name and new_name != "Bobo":
            return False

    if new_name:
        users[id]["name"] = new_name

    if new_password:
        users[id]["password"] = new_password

    if new_admin is not None:
        users[id]["admin"] = new_admin

    save_users(users)
    return True


# ============================================================
# 🔹 AUTH
# ============================================================
def authenticate(id, password):
    users = load_users()

    if id not in users or users[id]["password"] != password:
        return False

    return True, users[id]["admin"]


def change_password(id, old_password, new_password):
    users = load_users()

    if id not in users:
        return False

    if users[id]["password"] != old_password:
        return False

    users[id]["password"] = new_password
    save_users(users)
    return True


# ============================================================
# 🔹 BOBO
# ============================================================
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
