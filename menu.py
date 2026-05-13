import json
import os
import base64
import requests
import streamlit as st

MENU_FILE = "menu.json"
REPO = "monmirail6-dev/friterie"
FILE_PATH = "menu.json"

# ============================================================
# 🔹 LOAD MENU
# ============================================================
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
# 🔹 SAVE MENU (LOCAL + GITHUB)
# ============================================================
def save_menu():
    # local
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(Menu, f, indent=4, ensure_ascii=False)

    # github
    try:
        token = st.secrets["GITHUB_TOKEN"]

        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

        headers = {"Authorization": f"token {token}"}

        r = requests.get(url, headers=headers)
        data = r.json()

        sha = data["sha"]

        content_encoded = base64.b64encode(
            json.dumps(Menu, indent=4, ensure_ascii=False).encode()
        ).decode()

        requests.put(url, headers=headers, json={
            "message": "Update menu via Streamlit",
            "content": content_encoded,
            "sha": sha
        })

    except Exception as e:
        print("GitHub error:", e)

# ============================================================
# 🔹 INIT
# ============================================================
Menu = load_menu()

for key in ["Burgers", "Frites", "Sauces", "Suppléments", "Viandes"]:
    if key not in Menu:
        Menu[key] = {}

# ============================================================
# 🔹 CRUD
# ============================================================
def add_burger(name, price):
    if price <= 0:
        raise ValueError("Prix invalide")
    Menu["Burgers"][name] = price
    save_menu()

def modify_burger(old_name, new_name, new_price):
    if old_name not in Menu["Burgers"]:
        raise ValueError("Burger inexistant")

    if new_price <= 0:
        raise ValueError("Prix invalide")

    if new_name != old_name:
        del Menu["Burgers"][old_name]

    Menu["Burgers"][new_name] = new_price
    save_menu()

def del_burger(name):
    if name not in Menu["Burgers"]:
        raise ValueError("Burger inexistant")

    del Menu["Burgers"][name]
    save_menu()

def add_sauce(name):
    Menu["Sauces"][name] = 1.20
    save_menu()

def add_supp(name, price):
    if price <= 0:
        raise ValueError("Prix invalide")
    Menu["Suppléments"][name] = price
    save_menu()

def add_viande(name, price):
    if price <= 0:
        raise ValueError("Prix invalide")

    if "Viandes" not in Menu:
        Menu["Viandes"] = {}

    Menu["Viandes"][name] = price
    save_menu()
