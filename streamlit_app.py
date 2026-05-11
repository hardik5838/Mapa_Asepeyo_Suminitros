import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- 1. Page Configuration ---
st.set_page_config(page_title="Asepeyo Net Zero Map", layout="wide")
st.title("Asepeyo Center Infrastructure & Energy Map")

# --- 2. Color Mapping Functions ---
def get_rating_color(rating):
    """Maps energy ratings to Folium marker colors (Red to Green spectrum)"""
    rating = str(rating).strip().upper()
    colors = {
        'A': 'darkgreen', 'B': 'green', 'C': 'lightgreen', 
        'D': 'orange', 'E': 'lightred', 'F': 'red', 'G': 'darkred'
    }
    return colors.get(rating, 'gray')

def get_dist_color(dist):
    """Maps specific distributors to hex colors for the translucent layer"""
    dist = str(dist).lower()
    if 'endesa' in dist: return '#0056b3'    # Deep Blue
    if 'iberdrola' in dist: return '#28a745' # Forest Green
    if 'naturgy' in dist: return '#fd7e14'   # Orange
    if 'edp' in dist: return '#dc3545'       # Red
    if 'viesgo' in dist: return '#6f42c1'    # Purple
    if 'gaselec' in dist: return '#20c997'   # Teal
    return '#adb5bd'                         # Default Grey

# --- 3. Data Loading (Fetching from GitHub) ---
@st.cache_data
def load_data():
    # URL to the RAW data on GitHub
    github_url = "https://raw.githubusercontent.com/hardik5838/Mapa_Asepeyo_Suminitros/refs/heads/main/data.csv"
    
    try:
        df = pd.read_csv(github_url)
        
        # Parse 'Geo-Loaction' into separate Latitude and Longitude columns
        if 'Geo-Loaction' in df.columns:
            coords = df['Geo-Loaction'].astype(str).str.split(',', expand=True)
            if coords.shape[1] >= 2:
                df['Latitude'] = pd.to_numeric(coords[0], errors='coerce')
                df['Longitude'] = pd.to_numeric(coords[1], errors='coerce')
                
        return df
        
    except Exception as e:
        st.warning(f"⚠️ Could not load from GitHub. Error: {e}")
        # Dummy data fallback
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

# --- 4. Top Level Filters ---
st.header("Filter Centers")
col1, col2, col3 = st.columns(3)

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

# --- 5. Interactive Map Configuration ---
st.header("Interactive Map")
# Center the map on Spain
m = folium.Map(location=[40.4637, -3.7492], zoom_start=6, tiles="CartoDB positron")

# Layer 1: Distributor Regional Masks (Grouped into Big 3 + Others)
mask_layers = {
    'Endesa': folium.FeatureGroup(name="Zona: e-distribución (Endesa)", show=True),
    'Iberdrola': folium.FeatureGroup(name="Zona: i-DE (Iberdrola)", show=True),
    'Naturgy': folium.FeatureGroup(name="Zona: UFD (Naturgy)", show=True),
    'Others': folium.FeatureGroup(name="Zona: Otras", show=True)
}

for idx, row in filtered_df.iterrows():
    if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
        dist = str(row.get('Distribuidora Eléctrica', 'Unknown'))
        dist_lower = dist.lower()
        
        # Route the center to the correct concise layer group
        if 'endesa' in dist_lower:
            layer_group = mask_layers['Endesa']
        elif 'iberdrola' in dist_lower:
            layer_group = mask_layers['Iberdrola']
        elif 'naturgy' in dist_lower:
            layer_group = mask_layers['Naturgy']
        else:
            layer_group = mask_layers['Others']
            
        # The 45km radius creates the overlapping regional mask / small islands effect
        folium.Circle(
            location=[row['Latitude'], row['Longitude']],
            radius=45000, 
            color=None,
            fill=True,
            fill_color=get_dist_color(dist),
            fill_opacity=0.25,
            tooltip=f"Distributor: {dist}"
        ).add_to(layer_group)

# Add grouped mask layers to the map
for layer in mask_layers.values():
    layer.add_to(m)

# Layer 2: Center Markers (Smaller, compact points colored by Energy Rating)
pins_layer = folium.FeatureGroup(name="📍 Mostrar/Ocultar Puntos", show=True)

for idx, row in filtered_df.iterrows():
    if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
        
        # Determine the color based on the Energy Rating
        rating_val = row.get('Energy Rating', 'Pending')
        pin_color = get_rating_color(rating_val)
        gmaps_link = f"https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}"

        
        # HTML formatting for the popup
        popup_info = f"""
        <div style="font-family: Arial, sans-serif; min-width: 220px;">
            <h4 style="margin-bottom: 5px; color: #004b87;">{row.get('Centre', 'Unknown')}</h4>
            <hr style="margin: 5px 0;">
            <b>CUPS:</b> {row.get('CUPs', 'N/A')}<br>
            <b>Rating:</b> <span style="background-color: {pin_color}; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;">{rating_val}</span><br>
            <b>Audit:</b> {row.get('Audit Status', 'N/A')}<br>
            <b>Distributor:</b> {row.get('Distribuidora Eléctrica', 'N/A')}
            <a href="{gmaps_link}" target="_blank" style="text-decoration: none; color: #0056b3; font-weight: bold;">📍 Open in Google Maps</a>
        </div>
        """
        
        # Replaced bulky Marker with compact CircleMarker for a cleaner look
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            color="white",
            weight=1,
            fill=True,
            fill_color=pin_color,
            fill_opacity=1.0,
            popup=folium.Popup(popup_info, max_width=300),
            tooltip=row.get('Centre', 'Asepeyo Center')
        ).add_to(pins_layer)

pins_layer.add_to(m)

# Add layer control menu (Collapsed to prevent blocking the map!)
folium.LayerControl(position='topright', collapsed=True).add_to(m)

# Render map in Streamlit (returned_objects=[] speeds up the app significantly)
st_folium(m, width=1200, height=650, returned_objects=[])

# --- 6. Data Table and Export ---
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
