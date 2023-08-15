# Import required packages
from geopy.geocoders import ArcGIS
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import pyarrow as pa
import ezodf
import numpy as np

page_title = "Geo localistion of parc regional locations in France"
layout = "centered"

def main():
    st.set_page_config(page_title = page_title, layout = layout)
    st.title(page_title)

if __name__ == '__main__':
    main()

# --- Hide Streamlit Style ---
hide_st_style = """
                <style>
                #MainMenu {Visibility: hidden;}
                footer {Visibility: hidden;}
                header {Visibility: hidden;}
                </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

nom=ArcGIS()

# Read from file the parc regional locations in France
doc = ezodf.opendoc('parc_regional.ods')
print("Spreadsheet contains %d sheet(s)." % len(doc.sheets))
for sheet in doc.sheets:
    print("-"*40)
    print("   Sheet name : '%s'" % sheet.name)
    print("Size of Sheet : (rows=%d, cols=%d)" % (sheet.nrows(), sheet.ncols()) )

# convert the first sheet to a pandas.DataFrame
sheet = doc.sheets[0]
df_dict = {}
for i, row in enumerate(sheet.rows()):
    # row is a list of cells
    # assume the header is on the first row
    if i == 0:
        # columns as lists in a dictionary
        df_dict = {cell.value:[] for cell in row}
        # create index for the column headers
        col_index = {j:cell.value for j, cell in enumerate(row)}
        continue
    for j, cell in enumerate(row):
        # use header instead of column index
        df_dict[col_index[j]].append(cell.value)
# and convert to a DataFrame
parcreg_df = pd.DataFrame(df_dict)

# Set index from column S.no
parcreg_df2 = parcreg_df.set_index('S.no')

parcreg_df2['coordinates']=parcreg_df2['Parc natural regional'].apply(nom.geocode)
#parcreg_df2['coordinates'].values
st.write('Parc regional in France dataframe')
parcreg_df2

# 
parcreg_df2 = parcreg_df2.dropna()

# Using lambda function to set the latitude of longitude in parc regional dataframe
parcreg_df2['latitude'] = parcreg_df2['coordinates'].apply(lambda x: x.latitude)
parcreg_df2['longitude'] = parcreg_df2['coordinates'].apply(lambda x: x.longitude)
"---"
st.write('Parc regional in France dataframe without null values')
parcreg_df2

# Create a list from parc regional dataframe with columns
# Parc natural regional, latitude, and longitude
regreserve_list = parcreg_df2[['Parc natural regional', 'latitude', 'longitude']].values.tolist()


# Plotting regional natural reserve in the map
m = folium.Map(location=[43.390971907, 6.341430152], zoom_start=7)
fg = folium.FeatureGroup(name = "Regional_natural_reserve")

"---"
st.write()
st.write('Map showing geo located parc regional in France')
for i in regreserve_list:
    fg.add_child(
        folium.Marker(
            location=[i[1],i[2]],
            popup=f"{i[0]},{i[1]},{i[2]}",
            tooltip=f"{i[0]}",
            icon=folium.Icon(color="green")            
        )
    )

out = st_folium(
    m,
    feature_group_to_add=fg,
    width=1200,
    height=500,
)
