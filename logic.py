import menu
import commandes


# ============================================================
# 🟩 REGROUPER BURGER + SUPPLÉMENTS
# ============================================================
def regrouper_burger_supps(panier):
    """
    Transforme une liste brute en liste structurée :
    [
        {"article": "Cheese (+ Bacon, Cheddar)", "prix": 9.50},
        {"article": "Frites", "prix": 3.00},
        ...
    ]
    """
    items_affichage = []
    total = 0
    i = 0

    while i < len(panier):
        item = panier[i]

        # --------------------------
        # 🍔 BURGER
        # --------------------------
        if item in menu.Menu["Burgers"]:
            prix_burger = menu.Menu["Burgers"][item]
            supplements = []
            j = i + 1

            # Récupérer les suppléments associés
            while j < len(panier) and panier[j] in menu.Menu["Suppléments"]:
                supplements.append(panier[j])
                j += 1

            prix_supp = sum(menu.Menu["Suppléments"][s] for s in supplements)
            prix_total = prix_burger + prix_supp

            label = item
            if supplements:
                label += " (+ " + ", ".join(supplements) + ")"

            items_affichage.append({
                "Article": label,
                "Prix (€)": f"{prix_total:.2f}"
            })

            total += prix_total
            i = j
            continue

        # --------------------------
        # 🍟 FRITES
        # --------------------------
        if item in menu.Menu["Frites"]:
            prix = menu.Menu["Frites"][item]
            items_affichage.append({"Article": item, "Prix (€)": f"{prix:.2f}"})
            total += prix

        # --------------------------
        # 🥫 SAUCES
        # --------------------------
        elif item in menu.Menu["Sauces"]:
            prix = menu.Menu["Sauces"][item]
            items_affichage.append({"Article": item, "Prix (€)": f"{prix:.2f}"})
            total += prix

        i += 1

    return items_affichage, total



# ============================================================
# 🟩 GÉNÉRER UN TICKET COMPLET
# ============================================================
def generer_ticket(matricule):
    """
    Retourne un ticket structuré :
    {
        "items": [...],
        "total": 12.50
    }
    """
    panier = commandes.commandes.get(matricule, [])
    items, total = regrouper_burger_supps(panier)

    return {
        "items": items,
        "total": f"{total:.2f}"
    }



# ============================================================
# 🟩 COMPTEUR GLOBAL (CUISINE)
# ============================================================
def compteur_global():
    """
    Retourne une liste :
    [
        {"Article": "Cheese", "Quantité": 4},
        {"Article": "Frites", "Quantité": 7},
        ...
    ]
    """
    compteur = {}

    for _, panier in commandes.commandes.items():
        for item in panier:
            compteur[item] = compteur.get(item, 0) + 1

    # Transformation en tableau exploitable
    recap = [{"Article": k, "Quantité": v} for k, v in compteur.items()]
    recap.sort(key=lambda x: x["Article"].lower())

    return recap



# ============================================================
# 🟩 AJOUTER UN ARTICLE
# ============================================================
def ajouter_item(matricule, item):
    commandes.new_command(matricule, item)



# ============================================================
# 🟩 SUPPRIMER UN ARTICLE (INTELLIGENT)
# ============================================================
def supprimer_item(matricule, item):
    """
    Supprime un item.
    Si c'est un burger → supprime aussi ses suppléments.
    """
    panier = commandes.commandes.get(matricule, [])

    # Trouver toutes les positions
    indices = [i for i, x in enumerate(panier) if x == item]
    if not indices:
        return False

    i = indices[0]

    # Si burger → supprimer aussi les suppléments
    if item in menu.Menu["Burgers"]:
        j = i + 1
        while j < len(panier) and panier[j] in menu.Menu["Suppléments"]:
            j += 1
        del panier[i:j]
    else:
        del panier[i]

    commandes.commandes[matricule] = panier
    return True



# ============================================================
# 🟩 MODIFIER BURGER + SUPPLÉMENTS
# ============================================================
def modifier_burger_supps(matricule, old_burger, old_supps, new_burger, new_supps):
    """
    Remplace un burger + ses suppléments par un nouveau.
    """
    # 1️⃣ supprimer l'ancien
    commandes.modify_command(matricule, old_burger, 0)
    for s in old_supps:
        commandes.modify_command(matricule, s, 0)

    # 2️⃣ ajouter le nouveau burger
    commandes.new_command(matricule, new_burger)

    # 3️⃣ ajouter les nouveaux suppléments
    for s in new_supps:
        commandes.new_command(matricule, s)

    return True
