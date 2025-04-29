from dataclasses import dataclass
from datetime import datetime

import numpy as np
from pyart.core.radar import Radar

from fields import Fields


@dataclass(frozen=True)
class ReflectivitySnapshot:
    timestamp: datetime
    site_id: str
    lat: np.ndarray
    lon: np.ndarray
    alt: np.ndarray
    dBZ: np.ndarray


def nexrad_radar_to_reflectivity_snapshot(
    timestamp: datetime,
    site_id: str,
    radar: Radar,
    threshold_dBZ: float,
    downsampling_factor: int,
) -> ReflectivitySnapshot:

    lat_sweeps, lon_sweeps, alt_sweeps, dBZ_sweeps = [], [], [], []

    for sweep_idx in range(radar.nsweeps):
        gate_lat, gate_lon, gate_alt = radar.get_gate_lat_lon_alt(sweep_idx)
        reflectivity = radar.get_field(sweep_idx, Fields.REFLECTIVITY.value)

        mask = reflectivity > threshold_dBZ
        lat_sweeps.append(gate_lat[mask])
        lon_sweeps.append(gate_lon[mask])
        alt_sweeps.append(gate_alt[mask])
        dBZ_sweeps.append(reflectivity[mask])

    lat_all = np.concatenate(lat_sweeps)
    lon_all = np.concatenate(lon_sweeps)
    alt_all = np.concatenate(alt_sweeps)
    dBZ_all = np.concatenate(dBZ_sweeps)

    if downsampling_factor > 1:
        n_points = len(dBZ_all)
        step = max(1, n_points // (n_points // downsampling_factor))
        indices = np.arange(0, n_points, step)

        lat_all = lat_all[indices]
        lon_all = lon_all[indices]
        alt_all = alt_all[indices]
        dBZ_all = dBZ_all[indices]

    return ReflectivitySnapshot(
        timestamp=timestamp,
        site_id=site_id,
        lat=lat_all.astype(np.float32),
        lon=lon_all.astype(np.float32),
        alt=alt_all.astype(np.float16),
        dBZ=dBZ_all.astype(np.float16),
    )
