import streamlit as st
import menu
import users
import commandes
import ui
import logic
import pandas as pd

# ============================================================
# 🔹 CSS
# ============================================================
ui.inject_css()

# ============================================================
# 🔹 CACHE
# ============================================================
menu_data = menu.load_menu()
all_users = users.users_list()

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
# ADMIN MODE
# ============================================================
if st.session_state.user_name == "Bobo" and st.session_state.user_id == "2641987":

    if not st.session_state.admin_mode:
        if st.sidebar.button("🛠️ Activer mode admin"):
            st.session_state.admin_mode = True
            st.rerun()
    else:
        if st.sidebar.button("❌ Quitter admin"):
            st.session_state.admin_mode = False
            st.rerun()

# ============================================================
# ADMIN PANEL
# ============================================================
if st.session_state.admin_mode:

    st.sidebar.title("🛠️ Admin")

    if st.sidebar.button("Reset commandes"):
        commandes.reset_command()
        st.success("Reset OK")

    # SYNC
    st.sidebar.markdown("---")
    if st.sidebar.button("💾 Sync GitHub"):
        if menu.sync_menu_github() and users.sync_users_github():
            st.success("✅ Sync OK")

# ============================================================
# ✅ SIDEBAR CLIENT (UNIQUE)
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    st.sidebar.title("📦 Commandes")

    action = st.sidebar.selectbox(
        "Gestion",
        [" ", "Nouvelle commande", "Afficher ticket"],
        key="client_action"
    )

    # PASSWORD
    st.sidebar.markdown("---")
    with st.sidebar.expander("🔐 Changer mot de passe"):
        old = st.text_input("Ancien", type="password", key="client_old")
        new = st.text_input("Nouveau", type="password", key="client_new")
        new2 = st.text_input("Confirmer", type="password", key="client_new2")

        if st.button("Changer", key="change_pwd"):
            if new == new2:
                users.change_password(st.session_state.user_id, old, new)
                st.success("OK")

    # LOGOUT
    st.sidebar.markdown("---")
    if st.sidebar.button("Déconnexion"):
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()

# ============================================================
# CLIENT (LOGIQUE)
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    uid = st.session_state.user_id

    # ✅ IMPORTANT : on NE remet PAS de selectbox ici

    if action == "Nouvelle commande":

        if "panier" not in st.session_state:
            st.session_state.panier = []

        def add(x):
            st.session_state.panier.append(x)
            st.rerun()

        ui.colonnes(menu_data["Burgers"], lambda n, p: add(n))
        ui.colonnes(menu_data["Suppléments"], lambda n, p: add(n))

        st.write("Panier:")
        for x in st.session_state.panier:
            st.write(x)

        if st.button("Valider"):
            commandes.add_command(uid, st.session_state.panier)
            st.session_state.panier = []
            st.rerun()

    if action == "Afficher ticket":
        t = logic.generer_ticket(uid)
        df = pd.DataFrame(t["items"])
        st.dataframe(df)

# ============================================================
# MENU GLOBAL
# ============================================================
st.header("📋 Menu")
ui.inject_css()

menu_data = menu.load_menu()

for cat, items in menu_data.items():
    ui.categorie(cat)
    ui.colonnes(items, lambda n, p: st.write(f"{n} - {p}€"))
