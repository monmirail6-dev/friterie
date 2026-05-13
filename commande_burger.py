import streamlit as st
import menu
import users
import commandes
import ui
import logic
import pandas as pd

# ============================================================
# 🔹 DATA
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

def find_user(name):
    for uid, data in all_users.items():
        if data["name"].lower() == name.lower():
            return uid, data
    return None, None


if st.session_state.user_id is None:

    tab1, tab2 = st.sidebar.tabs(["🔑 Login", "➕ Register"])

    with tab1:
        login_name = st.text_input("Nom", key="login_name")
        login_pass = st.text_input("Mot de passe", type="password", key="login_pass")

        if st.button("Connexion", key="btn_login"):
            uid, data = find_user(login_name)

            if uid is None:
                st.error("Nom inconnu")
            else:
                ok = users.authenticate(uid, login_pass)
                if ok:
                    st.session_state.user_id = uid
                    st.session_state.user_name = data["name"]
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect")

    with tab2:
        reg_name = st.text_input("Nom complet", key="reg_name")
        reg_pass1 = st.text_input("Mot de passe", type="password", key="reg_pass1")
        reg_pass2 = st.text_input("Confirmer", type="password", key="reg_pass2")

        if st.button("Créer compte", key="btn_register"):
            if reg_pass1 != reg_pass2:
                st.error("Mismatch")
            else:
                uid = users.create_user(reg_name, reg_pass1)
                st.success(f"Compte créé : {uid}")

# ============================================================
# ADMIN BUTTON
# ============================================================
if st.session_state.user_name == "Bobo" and st.session_state.user_id == "2641987":
    if st.sidebar.button("🛠️ Activer admin", key="btn_admin_on"):
        st.session_state.admin_mode = True


# ============================================================
# ADMIN PANEL
# ============================================================
if st.session_state.admin_mode:

    st.sidebar.title("🛠️ Admin")

    # USERS
    with st.sidebar.expander("👥 Users"):
        new_user = st.text_input("Nom", key="admin_user_name")
        new_pass = st.text_input("Pass", type="password", key="admin_user_pass")

        if st.button("Ajouter user", key="btn_add_user"):
            users.create_user(new_user, new_pass)
            st.success("✅ Ajouté")
            st.rerun()

    # MENU
    with st.sidebar.expander("🍔 Menu"):

        menu_data = menu.load_menu()

        # BURGER
        burger_name = st.text_input("Burger", key="admin_burger_name")
        burger_price = st.number_input("Prix", min_value=0.01, key="admin_burger_price")

        if st.button("Ajouter burger", key="btn_add_burger"):
            if burger_name in menu_data["Burgers"]:
                st.error("Existe déjà")
            else:
                menu.add_burger(burger_name, burger_price)
                st.success("✅ OK")
                st.rerun()

        # SAUCE
        sauce_name = st.text_input("Sauce", key="admin_sauce_name")

        if st.button("Ajouter sauce", key="btn_add_sauce"):
            if sauce_name in menu_data["Sauces"]:
                st.error("Existe déjà")
            else:
                menu.add_sauce(sauce_name)
                st.success("✅ OK")
                st.rerun()

        # SUPP
        supp_name = st.text_input("Supplément", key="admin_supp_name")
        supp_price = st.number_input("Prix supp", min_value=0.01, key="admin_supp_price")

        if st.button("Ajouter supp", key="btn_add_supp"):
            if supp_name in menu_data["Suppléments"]:
                st.error("Existe déjà")
            else:
                menu.add_supp(supp_name, supp_price)
                st.success("✅ OK")
                st.rerun()

    # SYNC
    st.sidebar.markdown("---")

    if st.sidebar.button("💾 Sync GitHub", key="btn_sync"):
        ok1 = menu.sync_menu_github()
        ok2 = users.sync_users_github()

        if ok1 and ok2:
            st.success("✅ Sync OK")
        else:
            st.error("❌ Erreur")


# ============================================================
# CLIENT
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    uid = st.session_state.user_id
    ui.inject_css()

    action = st.sidebar.selectbox(
        "Action",
        ["Nouvelle commande", "Ticket"],
        key="client_action"
    )

    # NEW ORDER
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

        st.subheader("🧺 Panier")

        for item in st.session_state.panier:
            st.write("-", item)

        if st.button("Valider", key="btn_valider"):
            commandes.add_command(uid, st.session_state.panier)
            st.session_state.panier = []
            st.success("✅ OK")
            st.rerun()

    # TICKET
    if action == "Ticket":
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
