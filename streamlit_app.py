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
    # URL to the RAW data on GitHub
    github_url = "https://raw.githubusercontent.com/hardik5838/Mapa_Asepeyo_Suminitros/refs/heads/main/data.csv"
    
    try:
        # Attempt to read the CSV directly from the GitHub repository
        df = pd.read_csv(github_url)
        
        # --- CRITICAL FIX: Parse 'Geo-Loaction' into Latitude and Longitude ---
        # The map needs separate math coordinates, but the CSV has "Lat, Lon" in one string
        if 'Geo-Loaction' in df.columns:
            # Split the string by the comma
            coords = df['Geo-Loaction'].astype(str).str.split(',', expand=True)
            if coords.shape[1] >= 2:
                # Convert the split text into decimal numbers
                df['Latitude'] = pd.to_numeric(coords[0], errors='coerce')
                df['Longitude'] = pd.to_numeric(coords[1], errors='coerce')
                
        return df
        
    except Exception as e:
        # Fallback to dummy data if the GitHub link fails
        st.warning(f"⚠️ Could not load from GitHub. Error: {e}")
        data = {
            'Centre': ['Vía Augusta 36', 'Vía Augusta 18', 'Coslada Hospital'],
            'Latitude': [41.3985, 41.3970, 40.4259],
            'Longitude': [2.1524, 2.1510, -3.5643],
            'CUPs': ['ES1234', 'ES5678', 'ES9012'],
            'Energy Rating': ['B', 'C', 'A'],
            'Distribuidora Eléctrica': ['Endesa', 'Iberdrola', 'Iberdrola']
        }
        return pd.DataFrame(data)

df = load_data()

# 3. Top Level Filters
st.header("Filter Centers")
col1, col2, col3 = st.columns(3)

# Filter using the exact column names from your Spanish CSV
with col1:
    elec_filter = st.multiselect("Electricity Distributor", df['Distribuidora Eléctrica'].dropna().unique() if 'Distribuidora Eléctrica' in df.columns else [])
with col2:
    comunidad_filter = st.multiselect("Region (Comunidad)", df['Comunidad'].dropna().unique() if 'Comunidad' in df.columns else [])
with col3:
    rating_filter = st.multiselect("Energy Rating", df['Energy Rating'].dropna().unique() if 'Energy Rating' in df.columns else [])

# Apply filters to dataframe
filtered_df = df.copy()
if elec_filter:
    filtered_df = filtered_df[filtered_df['Distribuidora Eléctrica'].isin(elec_filter)]
if comunidad_filter:
    filtered_df = filtered_df[filtered_df['Comunidad'].isin(comunidad_filter)]
if rating_filter:
    filtered_df = filtered_df[filtered_df['Energy Rating'].isin(rating_filter)]

# 4. Interactive Map Configuration
st.header("Interactive Map")
# Center the map on Spain
m = folium.Map(location=[40.4637, -3.7492], zoom_start=6)

# --- Add Distributor Regional Masks (Translucent Layer) ---
distributors = filtered_df['Distribuidora Eléctrica'].dropna().unique() if 'Distribuidora Eléctrica' in filtered_df.columns else []
for dist in distributors:
    # Each distributor gets its own toggleable layer
    dist_layer = folium.FeatureGroup(name=f"Zona: {dist}", show=True) 
    dist_color = get_dist_color(dist)
    dist_data = filtered_df[filtered_df['Distribuidora Eléctrica'] == dist]
    
    for _, row in dist_data.iterrows():
        if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
            folium.Circle(
                location=[row['Latitude'], row['Longitude']],
                radius=45000, # 45km radius to visually merge nearby regions
                color=None,
                fill=True,
                fill_color=dist_color,
                fill_opacity=0.25,
                tooltip=f"Distributor: {dist}"
            ).add_to(dist_layer)
    dist_layer.add_to(m)

# --- Add Center Markers ---
pins_layer = folium.FeatureGroup(name="📍 Centers (Energy Rating)", show=True)

# Add markers to the map
for idx, row in filtered_df.iterrows():
    
    # Check if the row actually has valid numbers for Latitude and Longitude
    if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
        
        # HTML formatting for the popup (Using real column names like 'Centre' and 'CUPs')
        popup_info = f"""
        <b>{row.get('Centre', 'Unknown')}</b><br>
        <b>CUPS:</b> {row.get('CUPs', 'N/A')}<br>
        <b>Rating:</b> {row.get('Energy Rating', 'N/A')}<br>
        <b>Audit:</b> {row.get('Audit Status', 'N/A')}<br>
        <b>Distributor:</b> {row.get('Distribuidora Eléctrica', 'N/A')}
        """
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_info, max_width=300),
            tooltip=row.get('Centre', 'Asepeyo Center'),
            icon=folium.Icon(color=get_rating_color(row.get('Energy Rating')), icon="info-sign")
        ).add_to(pins_layer)

pins_layer.add_to(m)

# Add layer control menu to the top right of the map
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Render map in Streamlit (returned_objects=[] speeds up the app significantly)
st_folium(m, width=1200, height=600, returned_objects=[])

# 5. Data Table and Export
st.header("Center Data")
# Hide the raw latitude/longitude columns from the table to keep it clean
display_df = filtered_df.drop(columns=['Latitude', 'Longitude'], errors='ignore')
st.dataframe(display_df, use_container_width=True)

# Generate CSV for download
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='asepeyo_filtered_centers.csv',
    mime='text/csv',
)
