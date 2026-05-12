import streamlit as st
import menu
import users
import commandes
import ui
import logic
import pandas as pd


# Toujours définir action pour éviter les NameError
action = None

# ============================================================
# 🔒 INITIALISATION — BOBO ADMIN
# ============================================================
users.create_bobo_admin()

# ============================================================
# 🔓 SESSION STATE
# ============================================================
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# ============================================================
# 🔐 LOGIN / REGISTER SIDEBAR
# ============================================================
st.sidebar.title("👤 Connexion")

all_users = users.users_list()

# Trouver un user via son nom
def find_user_by_name(name):
    for uid, data in all_users.items():
        if data["name"].lower() == name.lower():
            return uid, data
    return None, None

# Si pas connecté → afficher login + création de compte
if st.session_state.user_id is None:

    tab_login, tab_register = st.sidebar.tabs(["🔑 Se connecter", "➕ Créer un compte"])

    # --------------------------
    # 🔑 LOGIN
    # --------------------------
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

    # --------------------------
    # ➕ REGISTER
    # --------------------------
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
                st.sidebar.success(f"Compte créé ! Votre ID : {new_id}")
                st.sidebar.info("Vous pouvez maintenant vous connecter.")

# ============================================================
# 🟩 SI CONNECTÉ → AFFICHER WELCOME
# ============================================================
if st.session_state.user_id:

    st.markdown("---")
    st.markdown("<h1 style='text-align:center;'>🍟 Rond‑Point</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Friterie – Prise de commande</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ---- WELCOME AVEC LOGO DANS LE CADRE ----

    if st.session_state.user_id:
   
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
# 🟥 BOUTON MODE ADMIN (BOBO SEULEMENT)
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

    # --- Modifier un utilisateur ---
    with st.sidebar.expander("✏️ Modifier un utilisateur", expanded=False):

        user_names = [data["name"] for data in all_users.values()]
        user_to_mod = st.selectbox("Utilisateur", [" "] + user_names, key="admin_mod_select")

        if user_to_mod.strip() != " ":
            uid, data = find_user_by_name(user_to_mod)

            new_name_mod = st.text_input("Nouveau nom", key="admin_mod_name")
            new_pass_mod = st.text_input("Nouveau mot de passe", type="password", key="admin_mod_pass")

            if st.button("Modifier", key="admin_mod_button"):
                ok = users.modify_user(uid, new_name=new_name_mod if new_name_mod else None,
                                        new_password=new_pass_mod if new_pass_mod else None)
                if ok:
                    st.success("Utilisateur modifié.")
                else:
                    st.error("Impossible de modifier cet utilisateur.")

    # --- Supprimer un utilisateur ---
    with st.sidebar.expander("❌ Supprimer un utilisateur", expanded=False):

        user_to_del = st.selectbox("Utilisateur", [" "] + user_names, key="admin_del_select")

        if st.button("Supprimer", key="admin_del_button"):
            uid, _ = find_user_by_name(user_to_del)
            ok = users.delete_user(uid)
            if ok:
                st.success("Utilisateur supprimé.")
            else:
                st.error("Impossible de supprimer cet utilisateur.")

    st.sidebar.markdown("---")        
    # --- ajouter burger ---
    with st.sidebar.expander("➕ Ajouter un burger", expanded=False):
        new_burger = st.text_input("Nouveau burger", key="new_burger")
        price = st.number_input("Prix", min_value=0.01, step=0.01, key="new_price")

        if st.button("Ajouter le burger", key="admin_add_burger"):
            if not new_burger.strip():
                st.error("Nom invalide.")
            elif new_burger in menu.Menu["Burgers"]:
                st.error("Ce burger existe déjà.")
            else:
                menu.add_burger(new_burger, price)
                st.success(f"✅ Burger « {new_burger} » ajouté.")
                
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

    # Changer mot de passe
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

    st.sidebar.markdown("---")

    if st.sidebar.button("Déconnexion", key="client_logout"):
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()

# ============================================================
# 🟩 ESPACE CLIENT (COMMANDES)
# ============================================================
if st.session_state.user_id and not st.session_state.admin_mode:

    uid = st.session_state.user_id
    ui.inject_css()

    # --------------------------------------------------------
    # 🟢 NOUVELLE COMMANDE
    # --------------------------------------------------------
    if action == "Nouvelle commande":
        st.header("🧾 Nouvelle commande")

        if "panier" not in st.session_state:
            st.session_state.panier = []

        if "erreur_supp" in st.session_state:
            st.error(st.session_state["erreur_supp"])
            del st.session_state["erreur_supp"]

        def bouton_ajout_simple(nom, prix):
            if ui.bouton(f"{nom} — {prix:.2f} €", key=f"btn_{nom}"):
                st.session_state.panier.append(nom)
                st.rerun()

        def bouton_ajout_supp(nom, prix):
            if ui.bouton(f"{nom} — {prix:.2f} €", key=f"supp_{nom}"):

                panier = st.session_state.panier

                last_burger = None
                for i in range(len(panier) - 1, -1, -1):
                    if panier[i] in menu.Menu["Burgers"]:
                        last_burger = i
                        break
                    if panier[i] in menu.Menu["Frites"] or panier[i] in menu.Menu["Sauces"]:
                        break

                if last_burger is None:
                    st.session_state["erreur_supp"] = "❌ Ajoutez d'abord un burger avant un supplément."
                    st.rerun()

                supps = []
                for x in panier[last_burger + 1:]:
                    if x in menu.Menu["Suppléments"]:
                        supps.append(x)
                    else:
                        break

                if nom in supps:
                    st.session_state["erreur_supp"] = f"❌ Le supplément '{nom}' est déjà ajouté."
                    st.rerun()

                st.session_state.panier.append(nom)
                st.rerun()

        choix = st.radio("Choisir une catégorie",
                         ["🍔 Burger + Suppléments", "🍟 Frites", "🥫 Sauces"],
                         key="radio_categorie")

        if choix == "🍔 Burger + Suppléments":
            st.subheader("🍔 Burgers")
            ui.colonnes(menu.Menu["Burgers"], bouton_ajout_simple)

            st.subheader("➕ Suppléments")
            ui.colonnes(menu.Menu["Suppléments"], bouton_ajout_supp)

        if choix == "🍟 Frites":
            st.subheader("🍟 Frites")
            ui.colonnes(menu.Menu["Frites"], bouton_ajout_simple)

        if choix == "🥫 Sauces":
            st.subheader("🥫 Sauces")
            ui.colonnes(menu.Menu["Sauces"], bouton_ajout_simple)

        st.markdown("---")
        st.subheader("🧺 Panier actuel")

        if not st.session_state.panier:
            st.info("Panier vide.")
        else:
            for item in st.session_state.panier:
                st.write(f"- {item}")

            if ui.bouton("✅ Valider la commande", key="valider_cmd"):
                commandes.add_command(uid, st.session_state.panier)
                st.success("Commande envoyée !")
                st.session_state.panier = []
                st.rerun()

    # --------------------------------------------------------
    # ✏️ MODIFIER COMMANDE
    # --------------------------------------------------------
    if action == "Modifier commande":
        st.header("✏️ Modifier la commande")

        if uid not in commandes.commandes or not commandes.commandes[uid]:
            st.info("Aucune commande à modifier.")
        else:
            panier = commandes.commandes[uid]

            st.subheader("🔄 Modifier quantité / supprimer un article")

            item = st.selectbox("Article", list(set(panier)), key="mod_item")
            qty = st.number_input("Nouvelle quantité", min_value=0, value=1, key="mod_qty")

            if ui.bouton("Modifier quantité", key="mod_qty_btn"):
                commandes.modify_command(uid, item, qty)
                st.success("Quantité modifiée.")
                st.rerun()

            if ui.bouton("Supprimer cet article", key="mod_del_btn"):
                logic.supprimer_item(uid, item)
                st.success("Article supprimé.")
                st.rerun()

            st.markdown("---")

            st.subheader("🍔 Modifier un burger + ses suppléments")

            burgers = []
            i = 0
            while i < len(panier):
                if panier[i] in menu.Menu["Burgers"]:
                    supps = []
                    j = i + 1
                    while j < len(panier) and panier[j] in menu.Menu["Suppléments"]:
                        supps.append(panier[j])
                        j += 1
                    burgers.append((i, panier[i], supps))
                    i = j
                else:
                    i += 1

            if not burgers:
                st.info("Aucun burger dans la commande.")
            else:
                choix_b = st.selectbox(
                    "Choisir le burger",
                    [f"{b[1]} (suppléments : {', '.join(b[2]) if b[2] else 'aucun'})" for b in burgers],
                    key="mod_burger_select"
                )

                idx = [f"{b[1]} (suppléments : {', '.join(b[2]) if b[2] else 'aucun'})"
                       for b in burgers].index(choix_b)

                pos, old_burger, old_supps = burgers[idx]

                new_burger = st.selectbox("Nouveau burger", list(menu.Menu["Burgers"].keys()), key="mod_new_burger")

                st.write("### ➕ Modifier les suppléments")
                new_supps = []
                for s in menu.Menu["Suppléments"]:
                    if st.checkbox(s, value=(s in old_supps), key=f"mod_supp_{s}"):
                        new_supps.append(s)

                if ui.bouton("💾 Enregistrer", key="mod_save_btn"):
                    logic.modifier_burger_supps(uid, old_burger, old_supps, new_burger, new_supps)
                    st.success("Burger modifié.")
                    st.rerun()

    # --------------------------------------------------------
    # 🗑️ SUPPRIMER COMMANDE
    # --------------------------------------------------------
    if action == "Supprimer commande":
        st.header("🗑️ Supprimer la commande")

        if uid not in commandes.commandes or not commandes.commandes[uid]:
            st.info("Aucune commande à supprimer.")
        else:
            if ui.bouton("❌ Supprimer toute la commande", key="del_all_cmd"):
                commandes.delete_command(uid)
                st.success("Commande supprimée.")
                st.rerun()

    # --------------------------------------------------------
    # 🧾 AFFICHER TICKET
    # --------------------------------------------------------
    if action == "Afficher ticket":
        st.header("🧾 Ticket de caisse")

        if uid not in commandes.commandes or not commandes.commandes[uid]:
            st.info("Aucune commande.")
        else:
            ticket = logic.generer_ticket(uid)
            df = pd.DataFrame(ticket["items"])
            ui.tableau(df)
            st.markdown(f"### 💰 Total : **{ticket['total']} €**")

    # --------------------------------------------------------
    # 📊 COMMANDE TOTALE (CUISINE)
    # --------------------------------------------------------
    if action == "Afficher la commande totale":
        st.header("📊 Commande totale (cuisine)")

        recap = logic.compteur_global()
        if not recap:
            st.info("Aucune commande.")
        else:
            df = pd.DataFrame(recap)
            ui.tableau(df)

    # --------------------------------------------------------
    # 🧾 AFFICHER TOUTES LES COMMANDES
    # --------------------------------------------------------
    if action == "Afficher toutes les commandes":

        ui.inject_css()
        st.header("🧾 Toutes les commandes")

        if not commandes.commandes:
            st.info("Aucune commande enregistrée.")
        else:
            total_global = 0
            all_users = users.users_list()

            for uid, liste in commandes.commandes.items():

                nom = all_users.get(uid, {}).get("name", "Inconnu")
                st.markdown(f"## 👤 {nom} ({uid})")

                ticket = logic.generer_ticket(uid)
                df = pd.DataFrame(ticket["items"])
                ui.tableau(df)

                st.markdown(f"### 💰 Total : **{ticket['total']} €**")
                total_global += float(ticket["total"])

                st.markdown("---")

            st.markdown(f"# 🧮 Total général : **{total_global:.2f} €**")

# ============================================================
# 📋 MENU (AFFICHAGE GLOBAL — TOUJOURS VISIBLE)
# ============================================================
st.header("📋 Menu")
ui.inject_css()

for categorie, items in menu.Menu.items():
    ui.categorie(categorie)
    ui.colonnes(
        items,
        lambda nom, prix: st.markdown(
            f"<div class='menu-line'>{nom}<span class='menu-price'>{prix:.2f} €</span></div>",
            unsafe_allow_html=True
        )
    )
