import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- 1. Page Configuration ---
st.set_page_config(page_title="Asepeyo Net Zero Map", layout="wide")
st.title("Asepeyo Center Infrastructure & Energy Map")

# --- 2. Helper & Color Mapping Functions ---
def get_rating_color(rating):
    """Maps energy ratings to Folium marker colors (Red to Green spectrum)"""
    rating = str(rating).strip().upper()
    colors = {
        'A': 'darkgreen', 'B': 'green', 'C': 'lightgreen', 
        'D': 'orange', 'E': 'lightred', 'F': 'red', 'G': 'darkred'
    }
    return colors.get(rating, 'gray')

def get_dist_color(dist):
    """Maps specific electric distributors to hex colors for the translucent layer"""
    dist = str(dist).lower()
    if 'endesa' in dist: return '#0056b3'    # Deep Blue
    if 'iberdrola' in dist: return '#28a745' # Forest Green
    if 'naturgy' in dist: return '#fd7e14'   # Orange
    if 'edp' in dist: return '#dc3545'       # Red
    if 'viesgo' in dist: return '#6f42c1'    # Purple
    if 'gaselec' in dist: return '#20c997'   # Teal
    return '#adb5bd'                         # Default Grey

def get_gas_distributor(cups_gas):
    """Deduces the Spanish Gas Distributor based on the CUPS Gas prefix"""
    if pd.isna(cups_gas) or str(cups_gas).strip() == '':
        return 'No Gas Supply'
        
    prefix = str(cups_gas).strip().upper()[:6]
    
    nedgia_prefixes = ['ES0203', 'ES0217', 'ES0218', 'ES0219', 'ES0220', 'ES0221', 'ES0222', 'ES0223', 'ES0224', 'ES0226', 'ES0227', 'ES0230', 'ES0237', 'ES0239', 'ES0242']
    redexis_prefixes = ['ES0202', 'ES0204', 'ES0205', 'ES0206', 'ES0208', 'ES0209', 'ES0225', 'ES0228', 'ES0238']
    nortegas_prefixes = ['ES0201', 'ES0211', 'ES0212', 'ES0213', 'ES0214', 'ES0215', 'ES0229']
    mrg_prefixes = ['ES0234', 'ES0236']
    
    if prefix in nedgia_prefixes: return 'Nedgia (Naturgy)'
    if prefix in redexis_prefixes: return 'Redexis Gas'
    if prefix in nortegas_prefixes: return 'Nortegas'
    if prefix in mrg_prefixes: return 'Madrileña Red de Gas'
    if prefix == 'ES0207': return 'Gas Extremadura'
    
    return 'Other Gas Distributor'

# --- 3. Data Loading (Fetching from GitHub) ---
@st.cache_data
def load_data():
    github_url = "https://raw.githubusercontent.com/hardik5838/Mapa_Asepeyo_Suminitros/refs/heads/main/data.csv"
    
    try:
        df = pd.read_csv(github_url)
        
        # Parse 'Geo-Loaction' into separate Latitude and Longitude columns
        if 'Geo-Loaction' in df.columns:
            coords = df['Geo-Loaction'].astype(str).str.split(',', expand=True)
            if coords.shape[1] >= 2:
                df['Latitude'] = pd.to_numeric(coords[0], errors='coerce')
                df['Longitude'] = pd.to_numeric(coords[1], errors='coerce')
                
        # Automatically generate Gas Supplier column based on CUPS Gas
        if 'Cups Gas' in df.columns:
            df['Distribuidora Gas'] = df['Cups Gas'].apply(get_gas_distributor)
                
        return df
        
    except Exception as e:
        st.warning(f"⚠️ Could not load from GitHub. Error: {e}")
        return pd.DataFrame()

df = load_data()

# --- 4. Top Level Filters ---
st.header("Filter Centers")
col1, col2, col3, col4 = st.columns(4)

with col1:
    elec_filter = st.multiselect("Electricity Distributor", df['Distribuidora Eléctrica'].dropna().unique() if 'Distribuidora Eléctrica' in df.columns else [])
with col2:
    if 'Distribuidora Gas' in df.columns:
        # Filter out 'No Gas Supply' for a cleaner dropdown, but keep it an option if needed
        gas_options = df['Distribuidora Gas'].unique().tolist()
        gas_filter = st.multiselect("Gas Distributor", gas_options)
    else:
        gas_filter = []
with col3:
    comunidad_filter = st.multiselect("Region (Comunidad)", df['Comunidad'].dropna().unique() if 'Comunidad' in df.columns else [])
with col4:
    rating_filter = st.multiselect("Energy Rating", df['Energy Rating'].dropna().unique() if 'Energy Rating' in df.columns else [])

# Apply filters to dataframe
filtered_df = df.copy()
if elec_filter:
    filtered_df = filtered_df[filtered_df['Distribuidora Eléctrica'].isin(elec_filter)]
if gas_filter:
    filtered_df = filtered_df[filtered_df['Distribuidora Gas'].isin(gas_filter)]
if comunidad_filter:
    filtered_df = filtered_df[filtered_df['Comunidad'].isin(comunidad_filter)]
if rating_filter:
    filtered_df = filtered_df[filtered_df['Energy Rating'].isin(rating_filter)]

# --- 5. Interactive Map Configuration ---
st.header("Interactive Map")
# Center the map on Spain
m = folium.Map(location=[40.4637, -3.7492], zoom_start=6, tiles="CartoDB positron")

# Layer 1: Distributor Regional Masks
mask_layers = {
    'Endesa': folium.FeatureGroup(name="Zona Eléctrica: Endesa", show=True),
    'Iberdrola': folium.FeatureGroup(name="Zona Eléctrica: Iberdrola", show=True),
    'Naturgy': folium.FeatureGroup(name="Zona Eléctrica: Naturgy", show=True),
    'Others': folium.FeatureGroup(name="Zona Eléctrica: Otras", show=True)
}

for idx, row in filtered_df.iterrows():
    if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
        dist = str(row.get('Distribuidora Eléctrica', 'Unknown'))
        dist_lower = dist.lower()
        
        if 'endesa' in dist_lower: layer_group = mask_layers['Endesa']
        elif 'iberdrola' in dist_lower: layer_group = mask_layers['Iberdrola']
        elif 'naturgy' in dist_lower: layer_group = mask_layers['Naturgy']
        else: layer_group = mask_layers['Others']
            
        folium.Circle(
            location=[row['Latitude'], row['Longitude']],
            radius=45000, 
            color=None,
            fill=True,
            fill_color=get_dist_color(dist),
            fill_opacity=0.25,
            tooltip=f"Electric Distributor: {dist}"
        ).add_to(layer_group)

for layer in mask_layers.values():
    layer.add_to(m)

# Layer 2: Center Markers 
pins_layer = folium.FeatureGroup(name="📍 Mostrar/Ocultar Puntos", show=True)

for idx, row in filtered_df.iterrows():
    if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
        
        rating_val = row.get('Energy Rating', 'Pending')
        pin_color = get_rating_color(rating_val)
        gmaps_link = f"https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}"
        
        # Formatting for Electricity and Gas Info
        cups_elec = row.get('CUPs', 'N/A')
        dist_elec = row.get('Distribuidora Eléctrica', 'N/A')
        
        cups_gas = row.get('Cups Gas', 'N/A') if pd.notna(row.get('Cups Gas')) else 'No Gas Supply'
        dist_gas = row.get('Distribuidora Gas', 'N/A')
        
        # HTML formatting for the popup
        popup_info = f"""
        <div style="font-family: Arial, sans-serif; min-width: 250px;">
            <h4 style="margin-bottom: 5px; color: #004b87;">{row.get('Centre', 'Unknown')}</h4>
            <hr style="margin: 5px 0;">
            <span style="background-color: {pin_color}; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; float: right;">{rating_val}</span>
            <b>Audit Status:</b> {row.get('Audit Status', 'N/A')}<br><br>
            
            <b style="color: #d9534f;">⚡ Electricity</b><br>
            <b>CUPS:</b> {cups_elec}<br>
            <b>Supplier:</b> {dist_elec}<br><br>
            
            <b style="color: #5cb85c;">🔥 Gas</b><br>
            <b>CUPS:</b> {cups_gas}<br>
            <b>Supplier:</b> {dist_gas}<br><br>
            
            <a href="{gmaps_link}" target="_blank" style="text-decoration: none; color: #0056b3; font-weight: bold;">📍 Open in Google Maps</a>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            color="white",
            weight=1,
            fill=True,
            fill_color=pin_color,
            fill_opacity=1.0,
            popup=folium.Popup(popup_info, max_width=350),
            tooltip=row.get('Centre', 'Asepeyo Center')
        ).add_to(pins_layer)

pins_layer.add_to(m)

# Add layer control menu - Expanded and positioned on Top Left to avoid blocking the map
folium.LayerControl(position='topleft', collapsed=False).add_to(m)

st_folium(m, width=1200, height=650, returned_objects=[])

# --- 6. Data Table and Export ---
st.header("Center Data")
display_df = filtered_df.drop(columns=['Latitude', 'Longitude'], errors='ignore')
st.dataframe(display_df, use_container_width=True)

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='asepeyo_filtered_centers.csv',
    mime='text/csv',
)

