import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. Page Configuration
st.set_page_config(page_title="Asepeyo Net Zero Map", layout="wide")
st.title("Asepeyo Center Infrastructure & Energy Map")

# 2. Data Loading (Fetching from GitHub)
@st.cache_data
def load_data():
    # IMPORTANT: Replace this URL with the RAW link to your data.csv on GitHub
    # Example format: "https://raw.githubusercontent.com/username/repository/main/data.csv"
    github_url = "https://raw.githubusercontent.com/hardik5838/Mapa_Asepeyo_Suminitros/refs/heads/main/data.csv"
    
    try:
        # Attempt to read the CSV directly from the GitHub repository
        df = pd.read_csv(github_url)
        return df
        
    except Exception as e:
        # Fallback to dummy data if the GitHub link isn't set up yet or is private
        st.warning(f"⚠️ Could not load from GitHub yet. Please update the `github_url` variable. Showing sample data for now.")
        data = {
            'Center_Name': ['Vía Augusta 36', 'Vía Augusta 18', 'Coslada Hospital'],
            'Latitude': [41.3985, 41.3970, 40.4259],
            'Longitude': [2.1524, 2.1510, -3.5643],
            'CUPS': ['ES1234', 'ES5678', 'ES9012'],
            'Energy_Rating': ['B', 'C', 'A'],
            'Dist_Elec': ['Endesa', 'Iberdrola', 'Iberdrola'],
            'Dist_Gas': ['Nedgia', 'Redexis', 'Madrileña Red de Gas']
        }
        return pd.DataFrame(data)

df = load_data()

# 3. Top Level Filters
st.header("Filter Centers")
col1, col2, col3 = st.columns(3)

# Added error handling in case the CSV doesn't match the exact column names yet
with col1:
    elec_filter = st.multiselect("Electricity Distributor", df['Dist_Elec'].unique() if 'Dist_Elec' in df.columns else [])
with col2:
    gas_filter = st.multiselect("Gas Distributor", df['Dist_Gas'].unique() if 'Dist_Gas' in df.columns else [])
with col3:
    rating_filter = st.multiselect("Energy Rating", df['Energy_Rating'].unique() if 'Energy_Rating' in df.columns else [])

# Apply filters to dataframe
filtered_df = df.copy()
if elec_filter:
    filtered_df = filtered_df[filtered_df['Dist_Elec'].isin(elec_filter)]
if gas_filter:
    filtered_df = filtered_df[filtered_df['Dist_Gas'].isin(gas_filter)]
if rating_filter:
    filtered_df = filtered_df[filtered_df['Energy_Rating'].isin(rating_filter)]

# 4. Interactive Map Configuration
st.header("Interactive Map")
# Center the map on Spain
m = folium.Map(location=[40.4637, -3.7492], zoom_start=6)

# Add markers to the map
for idx, row in filtered_df.iterrows():
    # Use .get() to safely pull data in case column names vary slightly in your live CSV
    popup_info = f"""
    <b>{row.get('Center_Name', 'Unknown')}</b><br>
    <b>CUPS:</b> {row.get('CUPS', 'N/A')}<br>
    <b>Rating:</b> {row.get('Energy_Rating', 'N/A')}<br>
    <b>Elec:</b> {row.get('Dist_Elec', 'N/A')}<br>
    <b>Gas:</b> {row.get('Dist_Gas', 'N/A')}
    """
    
    # Only map rows that actually have coordinates
    if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_info, max_width=300),
            tooltip=row.get('Center_Name', 'Asepeyo Center'),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

# To add Distributor Regions, you would load a GeoJSON here using folium.GeoJson()

# Render map in Streamlit
st_folium(m, width=1200, height=600)

# 5. Data Table and Export
st.header("Center Data")
st.dataframe(filtered_df, use_container_width=True)

# Generate CSV for download
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='asepeyo_filtered_centers.csv',
    mime='text/csv',
)
