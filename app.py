import time
from dataclasses import asdict

import pandas as pd
import pydeck as pdk
import streamlit as st

from app_util import get_reflectivity_rgba, refl_snapshot_to_df
from buffer import NEXRADReflectivitySnapshotBuffer
from sites import RadarSite, radar_sites


# Radar Site Selector

st.write("# NEXRAD Radar Sites - West Coast")

df_sites = pd.DataFrame([asdict(site) for site in radar_sites])
df_sites["size"] = 25_000

pdk_id_sites = "radar-sites"

sites_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_sites,
    get_position=["lon", "lat"],
    get_color="[255, 75, 75]",
    pickable=True,
    auto_highlight=True,
    get_radius="size",
    id=pdk_id_sites,
)

sites_view = pdk.View(type="MapView", controller=False, id=pdk_id_sites)

sites_view_state = pdk.ViewState(
    latitude=40,
    longitude=-120,
    zoom=4,
    min_zoom=4,
    max_zoom=4,
    id=pdk_id_sites,
)

sites_map = pdk.Deck(
    layers=[sites_layer],
    views=[sites_view],
    initial_view_state=sites_view_state,
    tooltip={"text": "{id}"},
)

event = st.pydeck_chart(sites_map, on_select="rerun", selection_mode="single-object")
selected = event.selection.get("objects", {}).get(pdk_id_sites, [])
if selected:
    try:
        selected_site = event.selection["objects"][pdk_id_sites][0]
        st.session_state["curr_site"] = RadarSite(
            id=selected_site["id"],
            city=selected_site["city"],
            state=selected_site["state"],
            lat=selected_site["lat"],
            lon=selected_site["lon"],
            alt=selected_site["alt"],
        )
    except KeyError as e:
        st.error("Missing radar site in selection: {e}")

# Reflectivity Viewer

st.write("# Reflectivity Viewer")

if "curr_site" not in st.session_state:  # default current site
    st.session_state["curr_site"] = RadarSite(
        id="KSOX",
        city="Santa Ana Mountains",
        state="CA",
        lat=33.817,
        lon=-117.635,
        alt=3105,
    )
curr_site = st.session_state["curr_site"]

st.write(f"### {curr_site.id} - {curr_site.city}, {curr_site.state}")

if "refl_buffer" not in st.session_state:
    st.session_state["refl_buffer"] = NEXRADReflectivitySnapshotBuffer()

refl_buffer = st.session_state["refl_buffer"]

with st.spinner("Loading radar snapshots..."):
    start_time = time.time()
    snapshots = refl_buffer.get_snapshots(curr_site.id)  # cached
    load_time = time.time() - start_time
    st.toast(f"Loaded {len(snapshots)} snapshots in {load_time:.1f}s", icon="✅")

dfs_refl = {}
for ss in snapshots:
    threshold_dBZ = -20.0
    df_refl = refl_snapshot_to_df(ss)
    df_refl["color"] = df_refl["dBZ"].apply(lambda x: get_reflectivity_rgba(x, threshold_dBZ))
    dfs_refl[ss.timestamp] = df_refl

pdk_id_refl = "refl"

refl_view = pdk.View(type="MapView", controller=False, id=pdk_id_refl)

refl_view_state = pdk.ViewState(
    latitude=curr_site.lat,
    longitude=curr_site.lon,
    zoom=7,
    pitch=45,
    height=600,
    id=pdk_id_refl,
)


@st.fragment
def hourly_reflectivity():
    timestamp = st.select_slider(label="Select time", options=sorted(dfs_refl.keys()))
    df_refl = dfs_refl[timestamp]
    reflectivity_layer = pdk.Layer(
        "PointCloudLayer",
        data=df_refl,
        get_position=["lon", "lat", "alt"],
        get_color="color",
        point_size=2,
        id=pdk_id_refl,
    )
    refl_map = pdk.Deck(
        layers=[reflectivity_layer],
        views=[refl_view],
        initial_view_state=refl_view_state,
    )
    st.write(f"Displaying {dfs_refl[timestamp].shape[0]} points")
    st.pydeck_chart(refl_map)


hourly_reflectivity()
