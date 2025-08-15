import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from textwrap import dedent
from datetime import date, datetime
from io import BytesIO
import os


import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# File path for the Excel file
EXCEL_FILE = 'grocerie.xlsx'

# Hardcoded categories from Feuil1 to avoid reading issues
@st.cache_data
def load_categories():
    categories = {
        'Fruits': ['Banane', 'Mangue', 'Melon', 'Pastèque', 'Pêche', 'Nectarine', 'Orange', 'Avocado', 'Pomme', 'Autres'],
        'Légumes': ['Pomme de terre', 'Tomate', 'Oignions', 'carotte', 'patate douce', 'concombre', 'Poivron', 'courgette', 'Aubergine', 'Persille', 'Menthe', 'ail', 'citronne', 'haricot vert', 'citrouille', 'choux', 'Laitues', 'Maïs', 'Autres'],
        'Epices et sauces': ['Piment', 'Curcuma', 'Poivre', 'Gingembre', 'Cumin', 'Cannelle', 'Girofle', 'Thym', 'Laurier', 'Sels', 'Ketchup', 'Mayonnaise', 'Sauce Burger', 'Sauce Soja', 'Sauce Fromagères', 'Sauce tacos', 'Sauce Algériennes', 'Autres'],
        'Légumineuse': ['Pois chiche', 'haricot', 'Lentille', 'riz', 'fève', 'petit pois', 'Autres'],
        'Semoulerie': ['Les pates', 'semoules', 'Autres'],
        'Boulangerie & pâtisserie': ['farines', 'Finot', 'Farine complet', 'levures chimique', 'Margarine', 'Eau de fleur', 'Cacao', 'aromes', 'sucre vanille', 'flan', 'chocolat', 'crèmes', 'amidon', 'crème fraiche', 'lait poudre', 'lait concentré', 'tacos/chawarma', 'Autres'],
        'Fruits sec': ['Amande', 'noix', 'raisin sec', 'chia', 'cajou', 'pistache', 'pavot', 'cacahuète', 'Avoine', 'sésame', 'Autres'],
        'Générale': ['Huile de table', "Huile d'olive", 'vinaigre', 'sucre', 'sucre brune', 'thé', 'café', 'Pains', 'Autres'],
        'Produit laitiers': ['Lait', 'Yogourt', 'Préparation fromage', 'Jus', 'Autres'],
        'Petit déjeuner': ['Confiture', 'chocolat tartiner', 'Beurre', 'Fromage', 'Autres'],
        'Boucherie': ['Viande', 'Viande hachée', 'Dinde', 'Poulet', 'Dinde fumé', 'Charcuterie', 'Autres'],
        'poissonnerie': ['Sardines', 'Anchois', 'Crevettes', 'Calamar', 'Autres'],
        'Nettoyage': ['Eau de javel', 'Lessive liquide', 'Lessive poudre', 'Savon vaisselle', 'désodoriseur', 'matériels nettoyage', 'Autres'],
        'Hygiène': ['shampooing', 'savon', 'gel douche', 'rasoirs', 'déodorant', 'lingette', 'mouchoirs', 'couches', 'serviette', 'Gel nettoyant', 'dentifrice', 'brosse à dents', 'Papiers hygiénique', 'Gel intime', 'autres'],
        'divers': ['Sac poubelles', 'Autres']
    }
    return categories

# Function to load data from Feuil2
def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name='Feuil2', engine='openpyxl')
            # Clean columns: remove unnamed or empty columns
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            # Ensure columns
            expected_cols = ['Date', 'Marché', 'catégorie', 'sous-catégorie', 'Prix', 'référence ticket', 'Observation']
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None
            # Convert Date to datetime
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            # Fill NaN prices with 0
            df['Prix'] = df['Prix'].fillna(0).astype(float)
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement des données: {e}")
            return pd.DataFrame(columns=['Date', 'Marché', 'catégorie', 'sous-catégorie', 'Prix', 'référence ticket', 'Observation'])
    else:
        return pd.DataFrame(columns=['Date', 'Marché', 'catégorie', 'sous-catégorie', 'Prix', 'référence ticket', 'Observation'])

# Function to save data to Feuil2
def save_data(df):
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='Feuil2', index=False)
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde des données: {e}")

# Load categories
categories = load_categories()

# App title
st.title("Gestion des Dépenses - Groceries")

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Ajouter un Achat", "Voir/Supprimer Achats", "Budget", "Synthèses Mensuelles"])

# Page 1: Ajouter un Achat
if page == "Ajouter un Achat":
    st.header("Enregistrer un Nouvel Achat")
    with st.form(key='add_purchase'):
        today = date.today()
        purchase_date = st.date_input("Date", value=today)
        marche = st.text_input("Marché (ex: Marjane, BIM)")
        cat = st.selectbox("Catégorie", options=list(categories.keys()))
        sub_cat_options = categories.get(cat, [])
        sub = st.selectbox("Sous-catégorie", options=sub_cat_options)
        prix = st.number_input("Prix (MAD)", min_value=0.0, step=0.1)
        ref_ticket = st.text_input("Référence Ticket")
        observation = st.text_area("Observation")
        submit = st.form_submit_button("Ajouter")
        
        if submit:
            new_data = {
                'Date': purchase_date,
                'Marché': marche,
                'catégorie': cat,
                'sous-catégorie': sub,
                'Prix': prix,
                'référence ticket': ref_ticket,
                'Observation': observation
            }
            df_data = load_data()
            df_data = pd.concat([df_data, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df_data)
            st.success("A