import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap


def refl_snapshot_to_df(ss):

    return pd.DataFrame(
        {
            "lat": ss.lat,
            "lon": ss.lon,
            "alt": ss.alt,
            "dBZ": ss.dBZ,
        }
    )


cmap = LinearSegmentedColormap.from_list(
    "ice",
    [
        (0.0, (1.0, 1.0, 1.0)),  # Pure white
        (0.5, (0.8, 0.9, 1.0)),  # Very light blue
        (1.0, (0.2, 0.5, 1.0)),  # Light blue
    ],
)


def get_reflectivity_rgba(dBZ: np.float16, threshold_dBZ: float):
    norm_dBZ = np.clip((dBZ - threshold_dBZ) / (80 - threshold_dBZ), 0, 1)
    rgba = cmap(norm_dBZ)

    min_opacity = 0.02
    max_opacity = 0.2
    norm_dBZ = norm_dBZ = np.clip((dBZ - threshold_dBZ) / (80 - threshold_dBZ), 0, 1)

    return [
        int(rgba[0] * 255),
        int(rgba[1] * 255),
        int(rgba[2] * 255),
        int((min_opacity + (max_opacity - min_opacity) * np.clip(norm_dBZ, 0, 1)) * 255),
    ]
