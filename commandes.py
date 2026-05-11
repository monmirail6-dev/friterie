commandes = {}

def new_command(name, item, qty=1):
    """Ajoute un item dans la liste du client."""
    if name not in commandes:
        commandes[name] = []

    for _ in range(qty):
        commandes[name].append(item)


def add_command(name, items):
    """Ajoute une liste d'items un par un."""
    if name not in commandes:
        commandes[name] = []

    for item in items:
        commandes[name].append(item)


def modify_command(name, item, new_qty):
    """Modifie la quantité d’un item (supprime puis réajoute)."""
    if name not in commandes:
        return

    commandes[name] = [i for i in commandes[name] if i != item]

    for _ in range(new_qty):
        commandes[name].append(item)


def delete_command(name, item=None):
    """Supprime un item ou toute la commande."""
    if name not in commandes:
        return

    if item is None:
        del commandes[name]
        return

    commandes[name] = [i for i in commandes[name] if i != item]

    if len(commandes[name]) == 0:
        del commandes[name]


def reset_command():
    """Supprime toutes les commandes."""
    commandes.clear()
