import streamlit as st
import math

# ============================================================
# 🎨 CSS GLOBAL (vert / noir)
# ============================================================
def inject_css():
    st.markdown("""
    <style>

    /* TITRES DE CATÉGORIES (menu) */
    .menu-category {
        color: #000000;
        background-color: #ffffff;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 22px;
        font-weight: 900;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* BOUTONS STREAMLIT — STYLE VERT/NOIR */
    div.stButton > button {
        background-color: #000000 !important;
        color: #00ff88 !important;
        border: 1px solid #00ff88 !important;
        padding: 8px 14px !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        width: 100% !important;
        text-align: left !important;
    }

    div.stButton > button:hover {
        background-color: #1a1a1a !important;
        color: #33ff99 !important;
        border-color: #33ff99 !important;
    }

    /* LIGNES DU MENU */
    .menu-line {
        display: inline-block;
        width: 100%;
        background: #000000;
        padding: 4px 8px;
        margin-bottom: 4px;
        border-radius: 6px;
        border: 1px solid #00ff88;
        color: #00ff88;
        font-size: 14px;
    }

    .menu-price {
        float: right;
        font-weight: 700;
        color: #b6ffda;
    }

    /* TABLEAUX VERT/NOIR */
    .box-green-black {
        background-color: #000000;
        border: 1px solid #00ff88;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 20px;
    }

    table {
        border-collapse: collapse;
        width: 100%;
    }

    th {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #00ff88 !important;
        font-weight: bold;
        padding: 6px;
    }

    td {
        background-color: #000000 !important;
        color: #00ff88 !important;
        border: 1px solid #00ff88 !important;
        padding: 6px;
    }

    </style>
    """, unsafe_allow_html=True)


# ============================================================
# 🟩 BOUTON PRO
# ============================================================
def bouton(label, key=None):
    """Bouton stylé vert/noir."""
    return st.button(label, key=key)


# ============================================================
# 🟩 TITRE DE CATÉGORIE (fond blanc)
# ============================================================
def categorie(titre):
    st.markdown(f"<div class='menu-category'>{titre}</div>", unsafe_allow_html=True)


# ============================================================
# 🟩 ENCADRÉ VERT/NOIR
# ============================================================
def encadre(html_content):
    st.markdown(f"<div class='box-green-black'>{html_content}</div>", unsafe_allow_html=True)


# ============================================================
# 🟩 TABLEAU VERT/NOIR
# ============================================================
def tableau(df):
    """Affiche un DataFrame dans un encadré vert/noir."""
    html = df.to_html(index=False, escape=False)
    encadre(html)


# ============================================================
# 🟩 COLONNES AUTOMATIQUES POUR MENU
# ============================================================
def colonnes(items_dict, callback, nb_cols=3):
    """
    Affiche un dictionnaire {nom: prix} en colonnes,
    trié par prix puis nom, et appelle callback(nom, prix).
    """
    items_sorted = sorted(items_dict.items(), key=lambda x: (x[1], x[0].lower()))
    cols = st.columns(nb_cols)
    chunk = math.ceil(len(items_sorted) / nb_cols)

    for col_idx in range(nb_cols):
        with cols[col_idx]:
            for nom, prix in items_sorted[col_idx * chunk:(col_idx + 1) * chunk]:
                callback(nom, prix)
