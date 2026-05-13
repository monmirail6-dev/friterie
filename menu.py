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

    # ✅ structure par défaut (important)
    return {
        "Burgers": {},
        "Frites": {},
        "Sauces": {},
        "Suppléments": {},
        "Viandes": {}
    }


# ============================================================
# 🔹 SAVE (LOCAL + GITHUB)
# ============================================================
def save_menu():

    # ✅ sauvegarde locale
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(Menu, f, indent=4, ensure_ascii=False)

    # ✅ push GitHub
    try:
        token = st.secrets["GITHUB_TOKEN"]

        url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

        headers = {
            "Authorization": f"token {token}"
        }

        # 🔹 récupérer SHA
        r = requests.get(url, headers=headers)
        data = r.json()

        sha = data["sha"]

        # 🔹 encoder contenu
        content_encoded = base64.b64encode(
            json.dumps(Menu, indent=4, ensure_ascii=False).encode()
        ).decode()

        commit_data = {
            "message": "Update menu via Streamlit",
            "content": content_encoded,
            "sha": sha
        }

        requests.put(url, headers=headers, json=commit_data)

    except Exception as e:
        print("⚠️ GitHub sync failed:", e)


# ============================================================
# 🔹 INIT MENU
# ============================================================
Menu = load_menu()

# Sécurité : s'assurer que toutes les clés existent
for key in ["Burgers", "Frites", "Sauces", "Suppléments", "Viandes"]:
    if key not in Menu:
        Menu[key] = {}


# ============================================================
# 🔹 CRUD MENU
# ============================================================

# --- Burger ---
def add_burger(name, price):
    if price <= 0:
        raise ValueError("Le prix doit être positif")

    Menu["Burgers"][name] = price
    save_menu()


def modify_burger(old_name, new_name, new_price):
    if old_name not in Menu["Burgers"]:
        raise ValueError(f"Le burger '{old_name}' n'existe pas.")

    if new_price <= 0:
        raise ValueError("Le prix doit être positif.")

    if new_name != old_name:
        del Menu["Burgers"][old_name]

    Menu["Burgers"][new_name] = new_price
    save_menu()


def del_burger(name):
    if name not in Menu["Burgers"]:
        raise ValueError(f"Le burger '{name}' n'existe pas.")

    del Menu["Burgers"][name]
    save_menu()


# --- Sauce ---
SAUCE_PRICE = 1.20

def add_sauce(name):
    Menu["Sauces"][name] = SAUCE_PRICE
    save_menu()


# --- Suppléments ---
def add_supp(name, price):
    if price <= 0:
        raise ValueError("Le prix doit être positif")

    Menu["Suppléments"][name] = price
    save_menu()


# --- Viandes ---
def add_viande(name, price):
    if price <= 0:
        raise ValueError("Le prix doit être positif")

    if "Viandes" not in Menu:
        Menu["Viandes"] = {}

    Menu["Viandes"][name] = price
    save_menu()
``
