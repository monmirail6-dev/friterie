import json
import os

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(Users, f, indent=4, ensure_ascii=False)

Users = load_users()


# ============================================================
# ➕ AJOUTER UN UTILISATEUR
# ============================================================
def add_user(matricule, name):
    if not (isinstance(matricule, str) and matricule.isdigit() and len(matricule) == 7):
        raise ValueError("Matricule invalide (7 chiffres requis)")

    if not name.strip():
        raise ValueError("Nom invalide")

    Users[matricule] = name.strip()
    save_users()


# ============================================================
# ✏️ MODIFIER UN UTILISATEUR
# ============================================================
def modify_user(matricule, name):
    if matricule not in Users:
        raise ValueError("Matricule inconnu")

    if not name.strip():
        raise ValueError("Nom invalide")

    Users[matricule] = name.strip()
    save_users()


# ============================================================
# ❌ SUPPRIMER UN UTILISATEUR
# ============================================================
def del_user(matricule):
    if matricule not in Users:
        raise ValueError("Matricule inconnu")

    del Users[matricule]
    save_users()