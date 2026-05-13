import streamlit as st
import menu
import users
import commandes
import ui
import logic
import pandas as pd
import os

token = st.secrets["GITHUB_TOKEN"]

# ✅ CSS (chargé une seule fois)
if "css_loaded" not in st.session_state:
    ui.inject_css()
    st.session_state.css_loaded = True

# Toujours définir action
action = None

# ✅ Nouveau menu chargé (cache)
menu_data = menu.load_menu()

# ============================================================
# 🔒 INIT
# ============================================================
users.create_bobo_admin()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# ============================================================
# LOGIN
# ============================================================
st.sidebar.title("👤 Connexion")

all_users = users.users_list()

def find_user_by_name(name):
    for uid, data in all_users.items():
        if data["name"].lower() == name.lower():
            return uid, data
    return None, None

if st.session_state.user_id is None:

    tab_login, tab_register = st.sidebar.tabs(["🔑 Se connecter", "➕ Créer un compte"])

    with tab_login:
        login_name = st.text_input("Nom", key="login_name")
        login_password = st.text_input("Mot de passe", type="password", key="login_password")

        if st.button("Connexion", key="login_button"):
            uid, data = find_user_by_name(login_name)

            if uid is None:
                st.sidebar.error("Nom inconnu.")
            else:
                ok = users.authenticate(uid, login_password)
                if ok:
                    st.session_state.user_id = uid
                    st.session_state.user_name = data["name"]
                    st.rerun()
                else:
                    st.sidebar.error("Mot de passe incorrect.")

    with tab_register:
        reg_name = st.text_input("Nom complet", key="reg_name")
        reg_pass = st.text_input("Mot de passe", type="password", key="reg_pass")
        reg_pass2 = st.text_input("Confirmer", type="password", key="reg_pass2")

        if st.button("Créer le compte", key="register_button"):
            if reg_pass != reg_pass2:
                st.sidebar.error("Mismatch")
            else:
                users.create_user(reg_name, reg_pass)
                st.sidebar.success("Compte créé")

# ============================================================
# WELCOME
# ============================================================
if st.session_state.user_id:

    st.markdown("---")
    st.markdown("<h1 style='text-align:center;'>🍟 Rond‑Point</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Friterie – Prise de commande</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(
        f"""
        <div style="background:#0d0d0d;padding:25px;border-radius:12px;text-align:center;
        color:#00ff88;border:2px solid #00ff88;box-shadow:0 0 12px rgba(0,255,136,0.25);margin-top:20px;">
            <h1 style="font-size:42px;margin:0;font-weight:900;letter-spacing:3px;">
                WELCOME {st.session_state.user_name.upper()}
            </h1>
            <p style="font-size:18px;margin-top:8px;color:#b6ffda;">
                ID : <strong>{st.session_state.user_id}</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# ADMIN MODE
# ============================================================
if st.session_state.user_name == "Bobo" and st.session_state.user_id == "2641987":

    if not st.session_state.admin_mode:
        if st.sidebar.button("🛠️ Activer mode admin", key="admin_on"):
            st.session_state.admin_mode = True
            st.rerun()
    else:
        if st.sidebar.button("❌ Quitter mode admin", key="admin_off"):
            st.session_state.admin_mode = False
            st.rerun()

# ============================================================
# ADMIN
# ============================================================
if st.session_state.admin_mode:

    # ✅ bouton GitHub
    st.sidebar.markdown("---")
    if st.sidebar.button("💾 Synchroniser avec GitHub", key="sync_github"):
        if menu.sync_menu_github() and users.sync_users_github():
            st.sidebar.success("✅ OK")

# ============================================================
# CLIENT SIDEBAR
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    st.sidebar.title("📦 Commandes")

    action = st.sidebar.selectbox(
        "Gestion",
        [" ", "Nouvelle commande", "Modifier commande", "Supprimer commande",
         "Afficher ticket", "Afficher la commande totale", "Afficher toutes les commandes"],
        key="client_action"
    )

    if st.sidebar.button("Déconnexion"):
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()

# ============================================================
# CLIENT LOGIQUE
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    uid = st.session_state.user_id

    if action == "Nouvelle commande":

        if "panier" not in st.session_state:
            st.session_state.panier = []

        def bouton(n):
            st.session_state.panier.append(n)
            st.rerun()

        ui.colonnes(menu_data["Burgers"], lambda n, p: bouton(n))
        ui.colonnes(menu_data["Suppléments"], lambda n, p: bouton(n))

        for x in st.session_state.panier:
            st.write(x)

        if st.button("Valider"):
            commandes.add_command(uid, st.session_state.panier)
            st.session_state.panier = []
            st.rerun()

# ============================================================
# MENU
# ============================================================
st.header("📋 Menu")

menu_data = menu.load_menu()

for categorie, items in menu_data.items():
    ui.categorie(categorie)
    ui.colonnes(
        items,
        lambda nom, prix: st.markdown(
            f"<div class='menu-line'>{nom}<span class='menu-price'>{prix:.2f} €</span></div>",
            unsafe_allow_html=True
        )
    )


