import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import time

st.set_page_config(page_title="Asepeyo Batch Geocoder", page_icon="📍", layout="wide")

st.title("📍 Asepeyo Batch Geocoder")
st.markdown("Upload your electricity/supply CSV, and this tool will automatically find the Latitude and Longitude for every center.")

# --- 1. File Upload ---
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # --- 2. Data Loading & Cleaning ---
    # Your specific CSV has 2 empty rows at the top before the real header
    skip_rows = st.number_input("Rows to skip at top of file (Set to 2 for your Electricidad CSV)", min_value=0, value=2)
    
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=skip_rows)
        else:
            df = pd.read_excel(uploaded_file, skiprows=skip_rows)
            
        st.success("File loaded successfully!")
        st.write("Preview of your data:")
        st.dataframe(df.head(3))
        
        # --- 3. Address Configuration ---
        st.subheader("⚙️ Configure Address Format")
        st.markdown("Select the columns that make up the full address. The tool will combine them.")
        
        # Try to auto-detect columns based on the Asepeyo file structure
        all_columns = df.columns.tolist()
        default_cols = [col for col in ['Dirección Suministro', 'CP', 'Provincia'] if col in all_columns]
        
        address_columns = st.multiselect(
            "Select columns to build the address:",
            options=all_columns,
            default=default_cols
        )
        
        country_suffix = st.text_input("Add a fixed suffix to help the map engine find it:", value="Spain")
        
        if address_columns:
            # Show an example of how the address will look
            sample_row = df.iloc[0].fillna("")
            sample_address = ", ".join([str(sample_row[col]) for col in address_columns])
            if country_suffix:
                sample_address += f", {country_suffix}"
            st.info(f"**Example Address:** {sample_address}")
            
            # --- 4. The Geocoding Engine ---
            if st.button("🚀 Start Geocoding (Takes ~3 minutes for 170 rows)", type="primary"):
                geolocator = Nominatim(user_agent="asepeyo_netzero_intern")
                
                # Setup progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                success_count = 0
                fail_count = 0
                
                latitudes = []
                longitudes = []
                full_addresses = []
                
                # Loop through every row
                for index, row in df.iterrows():
                    # Build the address string
                    parts = [str(row[col]) for col in address_columns if pd.notna(row[col])]
                    address = ", ".join(parts)
                    if country_suffix:
                        address += f", {country_suffix}"
                    
                    full_addresses.append(address)
                    
                    try:
                        # Request coordinates
                        location = geolocator.geocode(address, timeout=10)
                        
                        if location:
                            latitudes.append(location.latitude)
                            longitudes.append(location.longitude)
                            success_count += 1
                        else:
                            latitudes.append(None)
                            longitudes.append(None)
                            fail_count += 1
                            
                    except Exception as e:
                        latitudes.append(None)
                        longitudes.append(None)
                        fail_count += 1
                    
                    # MANDATORY 1-second sleep to respect OpenStreetMap's free server policy
                    time.sleep(1)
                    
                    # Update UI
                    progress = (index + 1) / len(df)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing row {index + 1}/{len(df)}... (Found: {success_count}, Failed: {fail_count})")
                
                # --- 5. Wrap up and Download ---
                df['Full_Search_Address'] = full_addresses
                df['Latitude'] = latitudes
                df['Longitude'] = longitudes
                
                st.success(f"✅ Geocoding Complete! Successfully mapped {success_count} centers. Could not find {fail_count} centers.")
                st.dataframe(df[['Name', 'Full_Search_Address', 'Latitude', 'Longitude']].head(10))
                
                # Generate Download
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download Final CSV with Coordinates",
                    data=csv_data,
                    file_name='Asepeyo_Centers_Geocoded.csv',
                    mime='text/csv'
                )
                
    except Exception as e:
        st.error(f"Error reading file: {e}")
