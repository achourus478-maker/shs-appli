import streamlit as st
import feedparser
import pandas as pd

# Configuration de l'interface
st.set_page_config(page_title="SHS Appels", page_icon="📚", layout="wide")

# CSS personnalisé pour un look académique
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stExpander { background-color: white; border-radius: 10px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600) # Rafraîchir toutes les heures
def get_calls():
    # Sources principales SHS
    urls = [
        "https://calenda.org/feed", 
        "https://journals.openedition.org/rss.php"
    ]
    all_entries = []
    
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title.lower()
            # Filtrage des appels à contributions
            if any(kw in title for kw in ["appel", "contribution", "varia", "numéro", "special issue", "colloque"]):
                category = "Général"
                if "hist" in title: category = "Histoire"
                elif "socio" in title: category = "Sociologie"
                elif "geo" in title: category = "Géographie"
                elif "philo" in title: category = "Philosophie"
                elif "art" in title: category = "Arts"
                
                all_entries.append({
                    "Titre": entry.title,
                    "Lien": entry.link,
                    "Discipline": category,
                    "Date": entry.get('published', 'Date non précisée')
                })
    return pd.DataFrame(all_entries)

# Titre de l'application
st.title("📚 SHS-Connect")
st.subheader("Veille automatisée des appels à articles en Sciences Humaines")

# Barre latérale
st.sidebar.header("Options de recherche")
df = get_calls()

disciplines = st.sidebar.multiselect("Filtrer par discipline :", options=df['Discipline'].unique(), default=[])

# Filtrage
if disciplines:
    df = df[df['Discipline'].isin(disciplines)]

# Affichage
st.write(f"### {len(df)} opportunités trouvées")

if not df.empty:
    for _, row in df.iterrows():
        with st.expander(f"📌 {row['Discipline'].upper()} : {row['Titre']}"):
            st.write(f"📅 Publié le : {row['Date']}")
            st.link_button("Consulter l'appel complet", row['Lien'])
else:
    st.info("Aucun appel ne correspond à vos critères actuels.")

st.sidebar.markdown("---")
st.sidebar.caption("Données extraites de Calenda et OpenEdition.")
