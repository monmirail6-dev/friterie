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
# 🟦 SIDEBAR ADMIN
# ============================================================
if st.session_state.admin_mode:

    st.sidebar.title("🛠️ Administration")

    # RESET COMMANDES
    if st.sidebar.button("♻️ Reset commandes", key="reset_cmd"):
        commandes.reset_command()
        st.sidebar.success("Toutes les commandes ont été réinitialisées.")

    st.sidebar.markdown("---")

    # LISTE USERS
    st.sidebar.subheader("👥 Utilisateurs")
    all_users = users.users_list()

    # --- Ajouter un utilisateur ---
    with st.sidebar.expander("➕ Ajouter un utilisateur", expanded=False):
        new_name = st.text_input("Nom", key="admin_add_name")
        new_pass = st.text_input("Mot de passe", type="password", key="admin_add_pass")

        if st.button("Créer utilisateur", key="admin_add_button"):
            if new_name.strip() == "":
                st.error("Nom invalide.")
            else:
                new_id = users.create_user(new_name, new_pass, admin=False)
                st.success(f"Utilisateur créé : {new_name} — ID : {new_id}")
                st.rerun()

    # --- Modifier un utilisateur ---
    with st.sidebar.expander("✏️ Modifier un utilisateur", expanded=False):

        user_names = [data["name"] for data in all_users.values()]
        user_to_mod = st.selectbox("Utilisateur", [" "] + user_names, key="admin_mod_select")

        if user_to_mod.strip() != " ":
            uid = None
            for i, d in all_users.items():
                if d["name"] == user_to_mod:
                    uid = i

            new_name_mod = st.text_input("Nouveau nom", key="admin_mod_name")
            new_pass_mod = st.text_input("Nouveau mot de passe", type="password", key="admin_mod_pass")

            if st.button("Modifier", key="admin_mod_button"):
                ok = users.modify_user(uid,
                    new_name=new_name_mod if new_name_mod else None,
                    new_password=new_pass_mod if new_pass_mod else None
                )

                if ok:
                    st.success("Utilisateur modifié.")
                    st.rerun()
                else:
                    st.error("Impossible de modifier cet utilisateur.")

    # --- Supprimer un utilisateur ---
    with st.sidebar.expander("❌ Supprimer un utilisateur", expanded=False):

        user_to_del = st.selectbox("Utilisateur", [" "] + user_names, key="admin_del_select")

        if st.button("Supprimer", key="admin_del_button"):
            uid = None
            for i, d in all_users.items():
                if d["name"] == user_to_del:
                    uid = i

            ok = users.delete_user(uid)

            if ok:
                st.success("Utilisateur supprimé.")
                st.rerun()
            else:
                st.error("Impossible de supprimer cet utilisateur.")

    st.sidebar.markdown("---")

    # ============================
    # 🍔 MENU
    # ============================
    with st.sidebar.expander("➕ Ajouter un item", expanded=False):

        menu_data = menu.load_menu()

        # --- BURGER ---
        new_burger = st.text_input("Nouveau burger", key="new_burger")
        burger_price = st.number_input("Prix", min_value=0.01, step=0.01, key="new_price")

        if st.button("Ajouter le burger", key="admin_add_burger"):
            if not new_burger.strip():
                st.error("Nom invalide.")
            elif new_burger in menu_data["Burgers"]:
                st.error("Ce burger existe déjà.")
            else:
                menu.add_burger(new_burger, burger_price)
                st.success(f"✅ Burger « {new_burger} » ajouté.")
                st.rerun()

        # --- SAUCE ---
        new_sauce = st.text_input("Nouvelle sauce", key="new_sauce")
        if st.button("Ajouter la sauce", key="admin_add_sauce"):
            if not new_sauce.strip():
                st.error("Nom invalide")
            elif new_sauce in menu_data["Sauces"]:
                st.error("Cette sauce existe déjà.")
            else:
                menu.add_sauce(new_sauce)
                st.success(f"✅ Sauce « {new_sauce} » ajoutée.")
                st.rerun()

        # --- SUPPLÉMENT ---
        new_supp = st.text_input("Nouveau supplément", key="new_supp")
        supp_price = st.number_input("Prix supplément", min_value=0.01, step=0.01, key="supp_price")

        if st.button("Ajouter le supplément", key="admin_add_supp"):
            if not new_supp.strip():
                st.error("Nom invalide.")
            elif new_supp in menu_data["Suppléments"]:
                st.error("Ce supplément existe déjà.")
            else:
                menu.add_supp(new_supp, supp_price)
                st.success(f"✅ Supplément « {new_supp} » ajouté.")
                st.rerun()

        # --- VIANDE ---
        new_viande = st.text_input("Nouvelle viande", key="new_viande")
        viande_price = st.number_input("Prix viande", min_value=0.01, step=0.01, key="viande_price")

        if st.button("Ajouter viande", key="admin_add_viande"):
            if not new_viande.strip():
                st.error("Nom invalide.")
            elif new_viande in menu_data.get("Viandes", {}):
                st.error("Cette viande existe déjà.")
            else:
                menu.add_viande(new_viande, viande_price)
                st.success(f"✅ Viande « {new_viande} » ajoutée.")
                st.rerun()

    # ============================
    # ✏️ MODIFIER BURGER
    # ============================
    with st.sidebar.expander("✏️ Modifier burger", expanded=False):

        menu_data = menu.load_menu()

        burgers = list(menu_data["Burgers"].keys())

        if burgers:
            burger_to_mod = st.selectbox("Burger", burgers, key="mod_burger_select")
            default_price = menu_data["Burgers"][burger_to_mod]

            new_name = st.text_input("Nouveau nom", key="mod_burger_name")
            new_price = st.number_input("Nouveau prix", value=default_price, min_value=0.01)

            if st.button("Modifier burger", key="mod_burger_btn"):
                final_name = new_name if new_name else burger_to_mod
                menu.modify_burger(burger_to_mod, final_name, new_price)
                st.success("✅ Modifié")
                st.rerun()
        else:
            st.info("Aucun burger")

    # ============================
    # 💾 SYNC GITHUB
    # ============================
    st.sidebar.markdown("---")

    if st.sidebar.button("💾 Synchroniser avec GitHub", key="sync_github"):
        ok1 = menu.sync_menu_github()
        ok2 = users.sync_users_github()

        if ok1 and ok2:
            st.sidebar.success("✅ Synchronisation OK")
        else:
            st.sidebar.error("❌ Erreur GitHub")

    # ============================
    # 🔌 DÉCONNEXION
    # ============================
    st.sidebar.markdown("---")

    if st.sidebar.button("Déconnexion", key="admin_logout"):
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.admin_mode = False
        st.rerun()
# ============================================================
# 🟩 SIDEBAR CLIENT (SI PAS ADMIN)
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    st.sidebar.title("📦 Commandes")

    action = st.sidebar.selectbox(
        "Gestion",
        [" ", "Nouvelle commande", "Modifier commande", "Supprimer commande",
         "Afficher ticket", "Afficher la commande totale", "Afficher toutes les commandes"],
        key="client_action"
    )

    # 🔐 CHANGER MOT DE PASSE
    st.sidebar.markdown("---")

    with st.sidebar.expander("🔐 Changer mot de passe", expanded=False):
        old = st.text_input("Ancien mot de passe", type="password", key="client_old_pass")
        new = st.text_input("Nouveau mot de passe", type="password", key="client_new_pass")
        new2 = st.text_input("Confirmer", type="password", key="client_new_pass2")

        if st.button("Changer mot de passe", key="client_change_pass"):
            if new != new2:
                st.error("Les mots de passe ne correspondent pas.")
            else:
                ok = users.change_password(st.session_state.user_id, old, new)
                if ok:
                    st.success("Mot de passe changé.")
                else:
                    st.error("Erreur : ancien mot de passe incorrect.")

    # ✅ DÉCONNEXION (REMIS)
    st.sidebar.markdown("---")

    if st.sidebar.button("Déconnexion", key="client_logout"):
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()


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
