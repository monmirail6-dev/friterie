import streamlit as st
import menu
import users
import commandes
import ui
import logic
import pandas as pd


# ============================================================
# 🔓 IDENTIFICATION UTILISATEUR
# ============================================================
if "matricule" not in st.session_state:
    st.session_state.matricule = None

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "name" not in st.session_state:
    st.session_state.name = None

matricule_input = st.sidebar.text_input("👤 N° de Matricule")

if matricule_input.isdigit() and len(matricule_input) == 7:
    st.session_state.matricule = matricule_input
    st.session_state.name = users.Users.get(matricule_input)

if st.session_state.matricule:
    if st.session_state.name:
        st.sidebar.success(f"Connecté en tant que {st.session_state.name}")
    else:
        st.sidebar.success("Connecté (matricule inconnu)")


# ============================================================
# 🏷️ EN-TÊTE
# ============================================================
st.markdown("---")
st.markdown("<h1 style='text-align:center;'>🍟 Rond‑Point</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Friterie – Prise de commande</p>", unsafe_allow_html=True)
st.markdown("---")

# Welcome
if st.session_state.matricule:
    st.markdown(
        f"""
        <div style="background:#0d0d0d;padding:25px;border-radius:12px;text-align:center;
        color:#00ff88;border:2px solid #00ff88;box-shadow:0 0 12px rgba(0,255,136,0.25);margin-top:20px;">
            <h1 style="font-size:42px;margin:0;font-weight:900;letter-spacing:3px;">
                ✈️ WELCOME {st.session_state.name.upper()}
            </h1>
            <p style="font-size:18px;margin-top:8px;color:#b6ffda;">
                Matricule : <strong>{st.session_state.matricule}</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 🔑 MODE ADMIN (SIDEBAR)
# ============================================================
ADMIN_PASSWORD = "OtSOtSOtS"

if st.session_state.matricule == "0501583":

    st.sidebar.markdown("### 🔧 Administration")

    if not st.session_state.admin_mode:
        pwd = st.sidebar.text_input("🔑 Admin password", type="password")
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_mode = True
            st.sidebar.success("🔑🔓 Mode admin activé")
            st.rerun()

    else:
        st.sidebar.success("🔑🔓 Mode admin activé")

        # RESET COMMANDES
        if st.sidebar.button("♻️ Reset commandes"):
            commandes.reset_command()
            st.sidebar.success("Toutes les commandes ont été réinitialisées")

        st.sidebar.markdown("---")

        # ADD / MODIFY BURGER
        st.sidebar.markdown("#### 🍔 Ajouter / Modifier un burger")

        burger_to_modify = st.sidebar.selectbox(
            "Burger à modifier",
            [" "] + list(menu.Menu["Burger"].keys())
        )

        new_burger_name = st.sidebar.text_input("Nouveau nom (laisser vide pour garder le même)")
        new_burger_price = st.sidebar.number_input("Nouveau prix", min_value=0.0, step=0.01)

        colA, colB = st.sidebar.columns(2)

        with colA:
            if st.sidebar.button("Ajouter"):
                try:
                    if new_burger_name.strip() == "":
                        st.sidebar.error("Veuillez entrer un nom pour le nouveau burger.")
                    else:
                        menu.add_burger(new_burger_name, new_burger_price)
                        st.sidebar.success("Burger ajouté.")
                except Exception as e:
                    st.sidebar.error(f"Erreur : {e}")

        with colB:
            if st.sidebar.button("Modifier"):
                try:
                    if burger_to_modify.strip() == " ":
                        st.sidebar.error("Sélectionnez un burger à modifier.")
                    else:
                        final_name = new_burger_name if new_burger_name.strip() != "" else burger_to_modify
                        menu.modify_burger(burger_to_modify, final_name, new_burger_price)
                        st.sidebar.success("Burger modifié.")
                except Exception as e:
                    st.sidebar.error(f"Erreur : {e}")

        st.sidebar.markdown("---")

        # DELETE BURGER
        st.sidebar.markdown("#### ❌ Supprimer un burger")

        burger_to_delete = st.sidebar.selectbox(
            "Burger à supprimer",
            [" "] + list(menu.Menu["Burger"].keys()),
            key="del_burger_select"
        )

        if st.sidebar.button("Supprimer burger", key="del_burger_btn"):
            try:
                if burger_to_delete.strip() == " ":
                    st.sidebar.error("Sélectionnez un burger à supprimer.")
                else:
                    menu.del_burger(burger_to_delete)
                    st.sidebar.success(f"Burger '{burger_to_delete}' supprimé.")
            except Exception as e:
                st.sidebar.error(f"Erreur : {e}")

        st.sidebar.markdown("---")

        # ADD SAUCE
        st.sidebar.markdown("#### 🥫 Ajouter une sauce")
        sauce_name = st.sidebar.text_input("Nom de la sauce")
        if st.sidebar.button("Ajouter sauce"):
            try:
                menu.add_sauce(sauce_name)
                st.sidebar.success("Sauce ajoutée")
            except Exception as e:
                st.sidebar.error(f"Erreur : {e}")

        st.sidebar.markdown("---")

        # ADD SUPPLEMENT
        st.sidebar.markdown("#### ➕ Ajouter un supplément")
        supp_name = st.sidebar.text_input("Nom du supplément")
        supp_price = st.sidebar.number_input("Prix du supplément", min_value=0.0, step=0.01)

        if st.sidebar.button("Ajouter supplément"):
            try:
                menu.add_supp(supp_name, supp_price)
                st.sidebar.success("Supplément ajouté")
            except Exception as e:
                st.sidebar.error(f"Erreur : {e}")

        st.sidebar.markdown("---")

        # ============================================================
        # 👥 GESTION DES UTILISATEURS (ADD / MODIFY / DELETE)
        # ============================================================

        st.sidebar.markdown("### 👥 Gestion des utilisateurs")

        # --- Ajouter un utilisateur ---
        st.sidebar.markdown("#### ➕ Ajouter un utilisateur")

        new_user_matricule = st.sidebar.text_input("Matricule (7 chiffres)", key="add_user_mat")
        new_user_name = st.sidebar.text_input("Nom complet", key="add_user_name")

        if st.sidebar.button("Ajouter utilisateur"):
            try:
                if not new_user_matricule.isdigit() or len(new_user_matricule) != 7:
                    st.sidebar.error("Le matricule doit contenir 7 chiffres.")
                elif new_user_name.strip() == "":
                    st.sidebar.error("Veuillez entrer un nom.")
                else:
                    users.add_user(new_user_matricule, new_user_name)
                    st.sidebar.success(f"Utilisateur {new_user_name} ajouté.")
            except Exception as e:
                st.sidebar.error(f"Erreur : {e}")

        # --- Modifier un utilisateur ---
        st.sidebar.markdown("#### ✏️ Modifier un utilisateur")

        user_to_modify = st.sidebar.selectbox(
            "Utilisateur à modifier",
            [" "] + list(users.Users.keys()),
            key="modify_user_select"
        )

        new_name_mod = st.sidebar.text_input("Nouveau nom", key="modify_user_name")

        if st.sidebar.button("Modifier utilisateur"):
            try:
                if user_to_modify.strip() == " ":
                    st.sidebar.error("Sélectionnez un utilisateur.")
                elif new_name_mod.strip() == "":
                    st.sidebar.error("Veuillez entrer un nouveau nom.")
                else:
                    users.modify_user(user_to_modify, new_name_mod)
                    st.sidebar.success("Utilisateur modifié.")
            except Exception as e:
                st.sidebar.error(f"Erreur : {e}")

        # --- Supprimer un utilisateur ---
        st.sidebar.markdown("#### ❌ Supprimer un utilisateur")

        user_to_delete = st.sidebar.selectbox(
            "Utilisateur à supprimer",
            [" "] + list(users.Users.keys()),
            key="delete_user_select"
        )

        if st.sidebar.button("Supprimer utilisateur"):
            try:
                if user_to_delete.strip() == " ":
                    st.sidebar.error("Sélectionnez un utilisateur.")
                else:
                    users.del_user(user_to_delete)
                    st.sidebar.success("Utilisateur supprimé.")
            except Exception as e:
                st.sidebar.error(f"Erreur : {e}")

        st.sidebar.markdown("---")

        if st.sidebar.button("Déconnexion"):
            st.session_state.admin_mode = False
            st.rerun()

# ============================================================
# 🎛️ MENU CLIENT
# ============================================================
action = None

if st.session_state.matricule and not st.session_state.admin_mode:
    action = st.sidebar.selectbox(
        "📦 Gestion de la commande",
        [" ", "Nouvelle commande", "Modifier commande", "Supprimer commande",
         "Afficher ticket", "Afficher la commande totale", "Afficher toutes les commandes"]
    )


# ============================================================
# 🧑‍🍳 ESPACE CLIENT
# ============================================================
if st.session_state.matricule and not st.session_state.admin_mode and action.strip():

    name = st.session_state.matricule
    ui.inject_css()

    # --------------------------------------------------------
    # 🟢 NOUVELLE COMMANDE
    # --------------------------------------------------------
    if action == "Nouvelle commande":

        st.header("🧾 Nouvelle commande")

        # Initialisation du panier
        if "panier" not in st.session_state:
            st.session_state.panier = []

        # Affichage des erreurs de supplément
        if "erreur_supp" in st.session_state:
            st.error(st.session_state["erreur_supp"])
            del st.session_state["erreur_supp"]

        # Bouton simple
        def bouton_ajout_simple(nom, prix):
            if ui.bouton(f"{nom} — {prix:.2f} €", key=f"btn_{nom}"):
                st.session_state.panier.append(nom)
                st.rerun()

        # Bouton intelligent pour suppléments
        def bouton_ajout_supp(nom, prix):
            if ui.bouton(f"{nom} — {prix:.2f} €", key=f"supp_{nom}"):

                panier = st.session_state.panier

                # Trouver le dernier burger
                last_burger = None
                for i in range(len(panier) - 1, -1, -1):
                    if panier[i] in menu.Menu["Burger"]:
                        last_burger = i
                        break
                    if panier[i] in menu.Menu["Frites"] or panier[i] in menu.Menu["Sauces"]:
                        break

                if last_burger is None:
                    st.session_state["erreur_supp"] = "❌ Ajoutez d'abord un burger avant un supplément."
                    st.rerun()

                # Vérifier doublon
                supps = []
                for x in panier[last_burger + 1:]:
                    if x in menu.Menu["Supplément"]:
                        supps.append(x)
                    else:
                        break

                if nom in supps:
                    st.session_state["erreur_supp"] = f"❌ Le supplément '{nom}' est déjà ajouté."
                    st.rerun()

                st.session_state.panier.append(nom)
                st.rerun()

        choix = st.radio("Choisir une catégorie",
                         ["🍔 Burger + Suppléments", "🍟 Frites", "🥫 Sauces"])

        if choix == "🍔 Burger + Suppléments":
            st.subheader("🍔 Burgers")
            ui.colonnes(menu.Menu["Burger"], bouton_ajout_simple)

            st.subheader("➕ Suppléments")
            ui.colonnes(menu.Menu["Supplément"], bouton_ajout_supp)

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

            if ui.bouton("✅ Valider la commande", key="valider"):
                commandes.add_command(name, st.session_state.panier)
                st.success("Commande envoyée !")
                st.session_state.panier = []
                st.rerun()

    # --------------------------------------------------------
    # ✏️ MODIFIER COMMANDE
    # --------------------------------------------------------
    if action == "Modifier commande":

        st.header("✏️ Modifier la commande")

        if name not in commandes.commandes or not commandes.commandes[name]:
            st.info("Aucune commande à modifier.")
        else:
            panier = commandes.commandes[name]

            st.subheader("🔄 Modifier quantité / supprimer un article")

            item = st.selectbox("Article", list(set(panier)))
            qty = st.number_input("Nouvelle quantité", min_value=0, value=1)

            if ui.bouton("Modifier quantité"):
                commandes.modify_command(name, item, qty)
                st.success("Quantité modifiée.")
                st.rerun()

            if ui.bouton("Supprimer cet article"):
                logic.supprimer_item(name, item)
                st.success("Article supprimé.")
                st.rerun()

            st.markdown("---")

            # Modifier burger + suppléments
            st.subheader("🍔 Modifier un burger + ses suppléments")

            burgers = []
            i = 0
            while i < len(panier):
                if panier[i] in menu.Menu["Burger"]:
                    supps = []
                    j = i + 1
                    while j < len(panier) and panier[j] in menu.Menu["Supplément"]:
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
                    [f"{b[1]} (suppléments : {', '.join(b[2]) if b[2] else 'aucun'})" for b in burgers]
                )

                idx = [f"{b[1]} (suppléments : {', '.join(b[2]) if b[2] else 'aucun'})"
                       for b in burgers].index(choix_b)

                pos, old_burger, old_supps = burgers[idx]

                new_burger = st.selectbox("Nouveau burger", list(menu.Menu["Burger"].keys()))

                st.write("### ➕ Modifier les suppléments")
                new_supps = []
                for s in menu.Menu["Supplément"]:
                    if st.checkbox(s, value=(s in old_supps)):
                        new_supps.append(s)

                if ui.bouton("💾 Enregistrer"):
                    logic.modifier_burger_supps(name, old_burger, old_supps, new_burger, new_supps)
                    st.success("Burger modifié.")
                    st.rerun()

    # --------------------------------------------------------
    # 🗑️ SUPPRIMER COMMANDE
    # --------------------------------------------------------
    if action == "Supprimer commande":
        st.header("🗑️ Supprimer la commande")

        if name not in commandes.commandes or not commandes.commandes[name]:
            st.info("Aucune commande à supprimer.")
        else:
            if ui.bouton("❌ Supprimer toute la commande"):
                commandes.delete_command(name)
                st.success("Commande supprimée.")
                st.rerun()

    # --------------------------------------------------------
    # 🧾 AFFICHER TICKET
    # --------------------------------------------------------
    if action == "Afficher ticket":
        st.header("🧾 Ticket de caisse")

        if name not in commandes.commandes or not commandes.commandes[name]:
            st.info("Aucune commande.")
        else:
            ticket = logic.generer_ticket(name)
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


# ============================================================
# 🧾 AFFICHER TOUTES LES COMMANDES
# ============================================================
if action == "Afficher toutes les commandes":

    ui.inject_css()
    st.header("🧾 Toutes les commandes")

    if not commandes.commandes:
        st.info("Aucune commande enregistrée.")
    else:
        total_global = 0

        for matricule, liste in commandes.commandes.items():

            nom = users.Users.get(matricule, "Inconnu")
            st.markdown(f"## 👤 {nom} ({matricule})")

            ticket = logic.generer_ticket(matricule)
            df = pd.DataFrame(ticket["items"])
            ui.tableau(df)

            st.markdown(f"### 💰 Total : **{ticket['total']} €**")
            total_global += float(ticket["total"])

            st.markdown("---")

        st.markdown(f"# 🧮 Total général : **{total_global:.2f} €**")


# ============================================================
# 📋 MENU (AFFICHAGE GLOBAL)
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