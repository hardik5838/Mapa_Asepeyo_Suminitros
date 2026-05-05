import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. Page Configuration
st.set_page_config(page_title="Asepeyo Net Zero Map", layout="wide")
st.title("Asepeyo Center Infrastructure & Energy Map")

# 2. Data Loading
@st.cache_data
def load_data():
    # Replace with your actual file path: pd.read_csv("asepeyo_centers.csv")
    # Using dummy data for demonstration
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

with col1:
    elec_filter = st.multiselect("Electricity Distributor", df['Dist_Elec'].unique())
with col2:
    gas_filter = st.multiselect("Gas Distributor", df['Dist_Gas'].unique())
with col3:
    rating_filter = st.multiselect("Energy Rating", df['Energy_Rating'].unique())

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
    # HTML formatting for the popup
    popup_info = f"""
    <b>{row['Center_Name']}</b><br>
    <b>CUPS:</b> {row['CUPS']}<br>
    <b>Rating:</b> {row['Energy_Rating']}<br>
    <b>Elec:</b> {row['Dist_Elec']}<br>
    <b>Gas:</b> {row['Dist_Gas']}
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_info, max_width=300),
        tooltip=row['Center_Name'],
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
