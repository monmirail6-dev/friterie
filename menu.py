import json
import os
import base64
import requests
import streamlit as st

MENU_FILE = "menu.json"
REPO = "monmirail6-dev/friterie"
FILE_PATH = "menu.json"


# ============================================================
# 🔹 LOAD (CACHÉ)
# ============================================================
@st.cache_data
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    return {
        "Burgers": {},
        "Frites": {},
        "Sauces": {},
        "Suppléments": {},
        "Viandes": {}
    }


# ============================================================
# 🔹 SAVE LOCAL
# ============================================================
def save_menu(menu_data):
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu_data, f, indent=4, ensure_ascii=False)

    # 🔥 reset cache
    load_menu.clear()


# ============================================================
# 🔹 SYNC GITHUB (MANUEL)
# ============================================================
def sync_menu_github():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {token}"}

        menu = load_menu()

        r = requests.get(url, headers=headers)
        data = r.json()
        sha = data["sha"]

        content_encoded = base64.b64encode(
            json.dumps(menu, indent=4, ensure_ascii=False).encode()
        ).decode()

        requests.put(url, headers=headers, json={
            "message": "Update menu via Streamlit",
            "content": content_encoded,
            "sha": sha
        })

        return True

    except Exception as e:
        print(e)
        return False


# ============================================================
# 🔹 CRUD
# ============================================================
def add_burger(name, price):
    menu = load_menu()

    if price <= 0:
        raise ValueError("Prix invalide")

    menu["Burgers"][name] = price
    save_menu(menu)


def modify_burger(old_name, new_name, new_price):
    menu = load_menu()

    if old_name not in menu["Burgers"]:
        raise ValueError("Burger inexistant")

    if new_price <= 0:
        raise ValueError("Prix invalide")

    if new_name != old_name:
        del menu["Burgers"][old_name]

    menu["Burgers"][new_name] = new_price
    save_menu(menu)


def del_burger(name):
    menu = load_menu()

    if name not in menu["Burgers"]:
        raise ValueError("Burger inexistant")

    del menu["Burgers"][name]
    save_menu(menu)


def add_sauce(name):
    menu = load_menu()
    menu["Sauces"][name] = 1.20
    save_menu(menu)


def add_supp(name, price):
    menu = load_menu()

    if price <= 0:
        raise ValueError("Prix invalide")

    menu["Suppléments"][name] = price
    save_menu(menu)


def add_viande(name, price):
    menu = load_menu()

    if price <= 0:
        raise ValueError("Prix invalide")

    if "Viandes" not in menu:
        menu["Viandes"] = {}

    menu["Viandes"][name] = price
    save_menu(menu)
