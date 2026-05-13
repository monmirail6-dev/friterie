import json
import os
import streamlit as st

MENU_FILE = "menu.json"

# Charger le menu depuis le fichier JSON
def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Sauvegarder le menu dans le fichier JSON
def save_menu():
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(Menu, f, indent=4, ensure_ascii=False)

# Charger le menu au démarrage
Menu = load_menu()

# Ajouter ou modifier un burger
def add_burger(name, price):
    if price <= 0:
        raise ValueError("Le prix doit être positif")
    Menu["Burgers"][name] = price
    save_menu()

# Ajouter une sauce
SAUCE_PRICE = 1.20
def add_sauce(name):
    Menu["Sauces"][name] = SAUCE_PRICE
    save_menu()

# Ajouter un supplément
def add_supp(name, price):
    if price <= 0:
        raise ValueError("Le prix doit être positif")
    Menu["Suppléments"][name] = price
    save_menu()

def add_viande(name, price):
    if price <= 0:
        raise ValueError("Le prix doit être positif")

    # Si la catégorie n'existe pas → on la crée
    if "Viandes" not in Menu:
        Menu["Viandes"] = {}

    Menu["Viandes"][name] = price
    save_menu()

def modify_burger(old_name, new_name, new_price):
    if old_name not in Menu["Burgers"]:
        raise ValueError(f"Le burger '{old_name}' n'existe pas.")
    if new_price <= 0:
        raise ValueError("Le prix doit être positif.")

    # Si le nom change
    if new_name != old_name:
        # On supprime l'ancien
        del Menu["Burgers"][old_name]
        # On crée le nouveau
        Menu["Burgers"][new_name] = new_price
    else:
        # On modifie juste le prix
        Menu["Burgers"][old_name] = new_price
    save_menu()

def del_burger(name):
    if name not in Menu["Burgers"]:
        raise ValueError(f"Le burger '{name}' n'existe pas.")
    del Menu["Burgers"][name]
    save_menu()

