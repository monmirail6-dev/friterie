import streamlit as st
import menu
import users
import commandes
import ui
import logic
import pandas as pd

# ============================================================
# 🔹 LOAD DATA (CACHE)
# ============================================================
menu_data = menu.load_menu()
all_users = users.users_list()

# ============================================================
# 🔒 INITIALISATION
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
# SIDEBAR LOGIN
# ============================================================
st.sidebar.title("👤 Connexion")


def find_user(name):
    for uid, data in all_users.items():
        if data["name"].lower() == name.lower():
            return uid, data
    return None, None


if st.session_state.user_id is None:

    tab1, tab2 = st.sidebar.tabs(["🔑 Login", "➕ Register"])

    with tab1:
        name = st.text_input("Nom")
        pwd = st.text_input("Mot de passe", type="password")

        if st.button("Connexion"):
            uid, data = find_user(name)

            if not uid:
                st.error("Nom inconnu")
            else:
                ok = users.authenticate(uid, pwd)
                if ok:
                    st.session_state.user_id = uid
                    st.session_state.user_name = data["name"]
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect")

    with tab2:
        n = st.text_input("Nom complet")
        p1 = st.text_input("Mot de passe", type="password")
        p2 = st.text_input("Confirmer", type="password")

        if st.button("Créer compte"):
            if p1 != p2:
                st.error("Mismatch")
            else:
                uid = users.create_user(n, p1)
                st.success(f"ID: {uid}")

# ============================================================
# ADMIN MODE
# ============================================================
if st.session_state.user_name == "Bobo" and st.session_state.user_id == "2641987":

    if st.sidebar.button("Activer admin"):
        st.session_state.admin_mode = True

# ============================================================
# SIDEBAR ADMIN
# ============================================================
if st.session_state.admin_mode:

    st.sidebar.title("🛠️ Admin")

    # -------- USERS --------
    with st.sidebar.expander("👥 Users"):
        user_names = [u["name"] for u in all_users.values()]

        name = st.text_input("Nom")
        pwd = st.text_input("Pass", type="password")

        if st.button("Ajouter user"):
            users.create_user(name, pwd)
            st.success("Ajouté")
            st.rerun()

    # -------- MENU --------
    with st.sidebar.expander("➕ Ajouter item"):

        menu_data = menu.load_menu()

        new_burger = st.text_input("Burger")
        price = st.number_input("Prix", 0.01)

        if st.button("Ajouter burger"):
            if new_burger in menu_data["Burgers"]:
                st.error("Existe")
            else:
                menu.add_burger(new_burger, price)
                st.success("OK")
                st.rerun()

        new_sauce = st.text_input("Sauce")

        if st.button("Ajouter sauce"):
            if new_sauce in menu_data["Sauces"]:
                st.error("Existe")
            else:
                menu.add_sauce(new_sauce)
                st.success("OK")
                st.rerun()

    # -------- SYNC --------
    st.sidebar.markdown("---")
    if st.sidebar.button("💾 Sync GitHub"):
        ok1 = menu.sync_menu_github()
        ok2 = users.sync_users_github()

        if ok1 and ok2:
            st.success("✅ Sync OK")
        else:
            st.error("❌ Erreur sync")

# ============================================================
# CLIENT
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    uid = st.session_state.user_id
    ui.inject_css()

    action = st.sidebar.selectbox(
        "Action",
        ["Nouvelle commande", "Afficher ticket"]
    )

    # -------- NEW COMMAND --------
    if action == "Nouvelle commande":

        if "panier" not in st.session_state:
            st.session_state.panier = []

        def add(n):
            st.session_state.panier.append(n)
            st.rerun()

        st.subheader("🍔 Burgers")
        ui.colonnes(menu_data["Burgers"], lambda n, p: add(n))

        st.subheader("➕ Suppléments")
        ui.colonnes(menu_data["Suppléments"], lambda n, p: add(n))

        st.subheader("🧺 Panier")
        for x in st.session_state.panier:
            st.write("-", x)

        if st.button("Valider"):
            commandes.add_command(uid, st.session_state.panier)
            st.session_state.panier = []
            st.success("✅ Commande envoyée")
            st.rerun()

    # -------- TICKET --------
    if action == "Afficher ticket":
        ticket = logic.generer_ticket(uid)
        df = pd.DataFrame(ticket["items"])
        st.dataframe(df)
        st.write("Total:", ticket["total"])

# ============================================================
# MENU GLOBAL
# ============================================================
st.header("📋 Menu")

menu_data = menu.load_menu()

for cat, items in menu_data.items():
    ui.categorie(cat)
    ui.colonnes(
        items,
        lambda n, p: st.markdown(
            f"<div>{n} - {p:.2f} €</div>",
            unsafe_allow_html=True
        )
    )
``
