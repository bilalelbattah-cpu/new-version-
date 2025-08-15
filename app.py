import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from textwrap import dedent
from datetime import date, datetime
from io import BytesIO
import os

Thought for 45spythonimport streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# File path for the Excel file (only for Feuil2, categories are hardcoded)
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
        'Générale': ['Huile de table', 'Huile d\'olive', 'vinaigre', 'sucre', 'sucre brune', 'thé', 'café', 'Pains', 'Autres'],  # Added Autres
        'Produit laitiers': ['Lait', 'Yogourt', 'Préparation fromage', 'Jus', 'Autres'],
        'Petit déjeuner': ['Confiture', 'chocolat tartiner', 'Beurre', 'Fromage', 'Autres'],
        'Boucherie': ['Viande', 'Viande hachée', 'Dinde', 'Poulet', 'Dinde fumé', 'Charcuterie', 'Autres'],
        'poissonnerie': ['Sardines', 'Anchois', 'Crevettes', 'Calamar', 'Autres'],
        'Nettoyage': ['Eau de javel', 'Lessive liquide', 'Lessive poudre', 'Savon vaisselle', 'désodoriseur', 'matériels nettoyage', 'Autres'],
        'Hygiène': ['shampooing', 'savon', 'gel douche', 'rasoirs', 'déodorant', 'lingette', 'mouchoirs', 'couches', 'serviette', 'Gel nettoyant', 'dentifrice', 'brosse à dents', 'Papiers hygiénique', 'Gel intime', 'autres'],
        'divers': ['Sac poubelles', 'Autres']
    }
    # Ensure 'Autres' is in each category
    for cat in categories:
        if 'Autres' not in categories[cat]:
            categories[cat].append('Autres')
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
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='Feuil2', index=False)

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
        prix = st.number_input("Prix", min_value=0.0, step=0.1)
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
            st.success("Achat ajouté avec succès !")
            st.rerun()

# Page 2: Voir/Supprimer Achats
elif page == "Voir/Supprimer Achats":
    st.header("Liste des Achats")
    df_data = load_data()
    if not df_data.empty:
        # Display editable table
        edited_df = st.data_editor(df_data, num_rows="dynamic", use_container_width=True)
        
        # Button to delete selected rows (using checkboxes)
        st.subheader("Supprimer des Achats")
        selected = st.multiselect("Sélectionnez les lignes à supprimer (par index)", options=df_data.index)
        if st.button("Supprimer les Sélectionnés"):
            df_data = df_data.drop(selected)
            save_data(df_data)
            st.success("Achats supprimés !")
            st.rerun()
    else:
        st.info("Aucun achat enregistré.")

# Page 3: Budget
elif page == "Budget":
    st.header("Gestion du Budget")
    df_data = load_data()
    
    # Set budgets (using session state for persistence, but for simplicity, hardcode or use inputs)
    if 'budgets' not in st.session_state:
        st.session_state.budgets = {cat: 0.0 for cat in categories}
    
    # Form to set budgets
    with st.form(key='set_budgets'):
        for cat in categories:
            st.session_state.budgets[cat] = st.number_input(f"Budget pour {cat}", value=st.session_state.budgets[cat], min_value=0.0)
        submit_budget = st.form_submit_button("Sauvegarder Budgets")
    
    # Calculate spent per category
    if not df_data.empty:
        spent = df_data.groupby('catégorie')['Prix'].sum().to_dict()
    else:
        spent = {cat: 0.0 for cat in categories}
    
    # Display budget status
    st.subheader("Statut du Budget")
    data = []
    for cat in categories:
        budget = st.session_state.budgets.get(cat, 0.0)
        spent_amount = spent.get(cat, 0.0)
        remaining = budget - spent_amount
        data.append([cat, budget, spent_amount, remaining])
    
    budget_df = pd.DataFrame(data, columns=['Catégorie', 'Budget', 'Dépensé', 'Restant'])
    st.table(budget_df)

# Page 4: Synthèses Mensuelles
elif page == "Synthèses Mensuelles":
    st.header("Synthèses Mensuelles")
    df_data = load_data()
    if not df_data.empty:
        # Extract month-year
        df_data['Mois'] = df_data['Date'].dt.strftime('%Y-%m')
        # Group by month and category
        summary = df_data.groupby(['Mois', 'catégorie'])['Prix'].sum().unstack().fillna(0)
        summary['Total'] = summary.sum(axis=1)
        
        # Display
        st.subheader("Dépenses par Mois et Catégorie")
        st.dataframe(summary)
        
        # Chart
        st.subheader("Graphique des Dépenses Mensuelles")
        st.line_chart(summary.drop('Total', axis=1))
        
        # Total per month
        st.subheader("Total par Mois")
        monthly_total = df_data.groupby('Mois')['Prix'].sum()
        st.bar_chart(monthly_total)
    else:
        st.info("Aucun données pour les synthèses.")
