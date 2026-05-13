import streamlit as st
import menu
import users
import commandes
import ui
import logic
import pandas as pd
import os

token = st.secrets["GITHUB_TOKEN"]

# ✅ CSS stable
if "css_loaded" not in st.session_state:
    ui.inject_css()
    st.session_state.css_loaded = True

action = None

# ✅ MENU CHARGÉ (IMPORTANT)
menu_data = menu.load_menu()

# ============================================================
# INIT
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
            if uid:
                ok = users.authenticate(uid, login_password)
                if ok:
                    st.session_state.user_id = uid
                    st.session_state.user_name = data["name"]
                    st.rerun()

# ============================================================
# WELCOME
# ============================================================
if st.session_state.user_id:
    st.markdown("<h1 style='text-align:center;'>🍟 Rond‑Point</h1>", unsafe_allow_html=True)

# ============================================================
# SIDEBAR CLIENT
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

    # ✅ IMPORTANT fix
    action = st.session_state.get("client_action")

    if action == "Nouvelle commande":

        st.header("🧾 Nouvelle commande")

        if "panier" not in st.session_state:
            st.session_state.panier = []

        def bouton_ajout_simple(nom, prix):
            if ui.bouton(f"{nom} — {prix:.2f} €", key=f"btn_{nom}"):
                st.session_state.panier.append(nom)
                st.rerun()

        def bouton_ajout_supp(nom, prix):
            if ui.bouton(f"{nom} — {prix:.2f} €", key=f"supp_{nom}"):

                panier = st.session_state.panier

                last_burger = None
                for i in range(len(panier) - 1, -1, -1):
                    if panier[i] in menu_data["Burgers"]:
                        last_burger = i
                        break

                if last_burger is None:
                    st.error("Ajoutez un burger d'abord")
                    return

                st.session_state.panier.append(nom)
                st.rerun()

        choix = st.radio(
            "Choisir une catégorie",
            ["🍔 Burger + Suppléments", "🍟 Frites", "🥫 Sauces"]
        )

        if choix == "🍔 Burger + Suppléments":
            ui.colonnes(menu_data["Burgers"], bouton_ajout_simple)
            ui.colonnes(menu_data["Suppléments"], bouton_ajout_supp)

        st.subheader("Panier")
        for item in st.session_state.panier:
            st.write(item)

        if st.button("Valider"):
            commandes.add_command(uid, st.session_state.panier)
            st.session_state.panier = []
            st.rerun()

    if action == "Afficher ticket":
        ticket = logic.generer_ticket(uid)
        df = pd.DataFrame(ticket["items"])
        st.dataframe(df)

# ============================================================
# ✅ GITHUB SYNC
# ============================================================
if st.session_state.admin_mode:
    if st.sidebar.button("💾 Sync GitHub"):
        menu.sync_menu_github()
        users.sync_users_github()

# ============================================================
# MENU GLOBAL
# ============================================================
st.header("📋 Menu")

for categorie, items in menu_data.items():
    ui.categorie(categorie)
    ui.colonnes(
        items,
        lambda nom, prix: st.markdown(
            f"<div class='menu-line'>{nom}<span class='menu-price'>{prix:.2f} €</span></div>",
            unsafe_allow_html=True
        )
    )

