import streamlit as st
import menu
import users
import commandes
import ui
import logic
import pandas as pd

# ============================================================
# 🔹 CSS (INCHANGÉ)
# ============================================================
ui.inject_css()

# ============================================================
# 🔹 CACHE MENU + USERS
# ============================================================
menu_data = menu.load_menu()
all_users = users.users_list()

# ============================================================
# 🔒 INIT BOBO
# ============================================================
users.create_bobo_admin()

# ============================================================
# SESSION STATE
# ============================================================
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# ============================================================
# LOGIN SIDEBAR
# ============================================================
st.sidebar.title("👤 Connexion")

def find_user_by_name(name):
    for uid, data in all_users.items():
        if data["name"].lower() == name.lower():
            return uid, data
    return None, None

# ============================================================
# LOGIN / REGISTER
# ============================================================
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
                    st.sidebar.success("Connexion réussie.")
                    st.rerun()
                else:
                    st.sidebar.error("Mot de passe incorrect.")

    with tab_register:
        reg_name = st.text_input("Nom complet", key="reg_name")
        reg_pass = st.text_input("Mot de passe", type="password", key="reg_pass")
        reg_pass2 = st.text_input("Confirmer le mot de passe", type="password", key="reg_pass2")

        if st.button("Créer le compte", key="register_button"):
            if reg_name.strip() == "":
                st.sidebar.error("Veuillez entrer un nom.")
            elif reg_pass != reg_pass2:
                st.sidebar.error("Les mots de passe ne correspondent pas.")
            else:
                new_id = users.create_user(reg_name, reg_pass, admin=False)
                st.sidebar.success(f"Compte créé ! ID : {new_id}")

# ============================================================
# ADMIN MODE
# ============================================================
if st.session_state.user_name == "Bobo" and st.session_state.user_id == "2641987":

    if not st.session_state.admin_mode:
        if st.sidebar.button("🛠️ Activer mode admin", key="admin_on"):
            st.session_state.admin_mode = True
            st.rerun()
    else:
        st.sidebar.success("Mode admin activé ✔")
        if st.sidebar.button("❌ Quitter mode admin", key="admin_off"):
            st.session_state.admin_mode = False
            st.rerun()

# ============================================================
# SIDEBAR ADMIN
# ============================================================
if st.session_state.admin_mode:

    st.sidebar.title("🛠️ Administration")

    # USERS
    with st.sidebar.expander("👥 Utilisateurs", expanded=False):
        new_name = st.text_input("Nom", key="admin_add_name")
        new_pass = st.text_input("Mot de passe", type="password", key="admin_add_pass")

        if st.button("Créer utilisateur", key="admin_add_button"):
            if new_name.strip():
                users.create_user(new_name, new_pass)
                st.success("Utilisateur créé")
                st.rerun()

    # MENU
    with st.sidebar.expander("➕ Ajouter un item", expanded=False):

        menu_data = menu.load_menu()

        new_burger = st.text_input("Nouveau burger", key="new_burger")
        price = st.number_input("prix", min_value=0.01, step=0.01, key="new_price")

        if st.button("Ajouter burger", key="add_burger"):
            if new_burger in menu_data["Burgers"]:
                st.error("Existe déjà")
            else:
                menu.add_burger(new_burger, price)
                st.success("✅ Ajouté")
                st.rerun()

        new_sauce = st.text_input("Nouvelle sauce", key="new_sauce")

        if st.button("Ajouter sauce", key="add_sauce"):
            if new_sauce in menu_data["Sauces"]:
                st.error("Existe déjà")
            else:
                menu.add_sauce(new_sauce)
                st.success("✅ Ajouté")
                st.rerun()

    # ✅ SYNC GITHUB (NOUVEAU)
    st.sidebar.markdown("---")

    if st.sidebar.button("💾 Sauvegarder sur GitHub", key="sync_github"):
        ok1 = menu.sync_menu_github()
        ok2 = users.sync_users_github()

        if ok1 and ok2:
            st.sidebar.success("✅ Sync OK")
        else:
            st.sidebar.error("❌ Erreur GitHub")

# ============================================================
# CLIENT
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    uid = st.session_state.user_id
    ui.inject_css()

    action = st.sidebar.selectbox(
        "Gestion",
        [" ", "Nouvelle commande", "Afficher ticket"],
        key="client_action"
    )

    # NOUVELLE COMMANDE
    if action == "Nouvelle commande":

        if "panier" not in st.session_state:
            st.session_state.panier = []

        def add_item(n):
            st.session_state.panier.append(n)
            st.rerun()

        st.subheader("🍔 Burgers")
        ui.colonnes(menu_data["Burgers"], lambda n, p: add_item(n))

        st.subheader("➕ Suppléments")
        ui.colonnes(menu_data["Suppléments"], lambda n, p: add_item(n))

        st.subheader("Panier")

        for item in st.session_state.panier:
            st.write("-", item)

        if st.button("Valider", key="valider_cmd"):
            commandes.add_command(uid, st.session_state.panier)
            st.session_state.panier = []
            st.rerun()

    # TICKET
    if action == "Afficher ticket":
        ticket = logic.generer_ticket(uid)
        df = pd.DataFrame(ticket["items"])
        ui.tableau(df)

# ============================================================
# MENU GLOBAL
# ============================================================
st.header("📋 Menu")
ui.inject_css()

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
