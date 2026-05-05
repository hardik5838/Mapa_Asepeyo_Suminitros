import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="Asepeyo Net Zero Map", layout="wide")
st.title("🏥 Asepeyo Net Zero: Infrastructure & Supply Map")
st.markdown("Upload your raw Electricidad CSV. The app will automatically find the centers and build your interactive dashboard.")

# --- 2. Data Upload & Smart Processing ---
uploaded_file = st.file_uploader("Upload your 'Electricidad...csv' file here", type=['csv'])

if uploaded_file is not None:
    # Read the file, skipping the two blank title rows at the top
    df = pd.read_csv(uploaded_file, skiprows=2)
    
    # We only want rows that are actually centers (drop empty rows)
    df = df.dropna(subset=['Centre'])
    
    # Create the "Smart Search" string to bypass messy street addresses
    # Format: "Asepeyo [Center Name], [Province], Spain"
    df['Smart_Address'] = "Asepeyo " + df['Centre'].astype(str) + ", " + df['Provincia'].astype(str) + ", Spain"
    
    # Add dummy columns for the extra data you requested (since they aren't in the Electricidad file)
    # You can replace these with real data merges later
    if 'Energy_Rating' not in df.columns:
        df['Energy_Rating'] = 'Pending Audit'
    if 'Dist_Elec' not in df.columns:
        df['Dist_Elec'] = 'Unknown (Check Bill)'
    if 'Dist_Gas' not in df.columns:
        df['Dist_Gas'] = 'Unknown (Check Bill)'
        
    st.success(f"Loaded {len(df)} centers. Ready to build map!")

    # --- 3. Geocoding Engine (Runs only once and saves to session state) ---
    if 'geocoded_data' not in st.session_state:
        if st.button("🚀 Initialize Map Coordinates (Takes ~2 minutes)"):
            geolocator = Nominatim(user_agent="asepeyo_dashboard_internal")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            latitudes = []
            longitudes = []
            
            for index, row in df.iterrows():
                try:
                    # Search using our clean "Smart Address"
                    location = geolocator.geocode(row['Smart_Address'], timeout=5)
                    if location:
                        latitudes.append(location.latitude)
                        longitudes.append(location.longitude)
                    else:
                        # Fallback: Just search "Asepeyo, [Province], Spain" if center name fails
                        fallback = f"Asepeyo, {row['Provincia']}, Spain"
                        loc_fallback = geolocator.geocode(fallback, timeout=5)
                        latitudes.append(loc_fallback.latitude if loc_fallback else None)
                        longitudes.append(loc_fallback.longitude if loc_fallback else None)
                except:
                    latitudes.append(None)
                    longitudes.append(None)
                
                time.sleep(1) # Mandatory pause for free map server
                progress = len(latitudes) / len(df)
                progress_bar.progress(progress)
                status_text.text(f"Mapping centers... {len(latitudes)}/{len(df)}")
            
            df['Latitude'] = latitudes
            df['Longitude'] = longitudes
            st.session_state['geocoded_data'] = df
            st.rerun()

    # --- 4. Interactive Dashboard (Renders after geocoding is done) ---
    if 'geocoded_data' in st.session_state:
        map_df = st.session_state['geocoded_data']
        
        # Filters
        st.sidebar.header("🔍 Filter Centers")
        estado_filter = st.sidebar.multiselect("Estado", map_df['Estado'].dropna().unique(), default=["Alta"])
        prov_filter = st.sidebar.multiselect("Provincia", map_df['Provincia'].dropna().unique())
        
        # Apply Filters
        filtered_df = map_df.copy()
        if estado_filter:
            filtered_df = filtered_df[filtered_df['Estado'].isin(estado_filter)]
        if prov_filter:
            filtered_df = filtered_df[filtered_df['Provincia'].isin(prov_filter)]

        # Drop rows that still couldn't be found
        valid_map_data = filtered_df.dropna(subset=['Latitude', 'Longitude'])
        
        st.subheader(f"🗺️ Map View ({len(valid_map_data)} Centers)")
        
        # Draw Map
        m = folium.Map(location=[40.4168, -3.7038], zoom_start=6, tiles="CartoDB positron")
        
        for idx, row in valid_map_data.iterrows():
            popup_html = f"""
            <div style="font-family: Arial; min-width: 250px;">
                <h4 style="color:#004b87; margin-bottom:5px;">{row['Centre']}</h4>
                <b>CUPS:</b> {row['Name']}<br>
                <b>Estado:</b> {row['Estado']}<br>
                <b>Energy Rating:</b> {row['Energy_Rating']}<br>
                <b>Elec. Dist.:</b> {row['Dist_Elec']}<br>
                <b>Gas Dist.:</b> {row['Dist_Gas']}<br>
                <hr style="margin: 5px 0;">
                <a href="#" target="_blank">View Audit Report</a> | <a href="#" target="_blank">BMS Logs</a>
            </div>
            """
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row['Centre'],
                icon=folium.Icon(color="blue", icon="building", prefix="fa")
            ).add_to(m)
            
        st_folium(m, width=1200, height=600, returned_objects=[])
        
        # Data Table and Export
        st.subheader("📊 Exportable Data Table")
        st.markdown("Filter the table above, then copy/paste or download the resulting data.")
        st.dataframe(filtered_df[['Name', 'Centre', 'Estado', 'Provincia', 'Dirección Suministro', 'Energy_Rating']], use_container_width=True)
        
        st.download_button(
            label="⬇️ Download Dashboard Data as CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='Asepeyo_Dashboard_Export.csv',
            mime='text/csv'
        )
