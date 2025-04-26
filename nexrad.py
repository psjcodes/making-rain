from datetime import datetime, timedelta, timezone
from typing import Dict, List

import fsspec
import pyart
import streamlit as st
from pyart.core.radar import Radar

from config import S3_BUCKET
from fields import Fields


@st.cache_data(ttl=300, show_spinner=False)
def get_hourly_nexrad_file_paths(
    site_id: str = "KSOX",
    prev_hours: int = 3,
) -> Dict[datetime, str]:
    fs = fsspec.filesystem("s3", anon=True)
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    paths = {}

    for hours_ago in range(1, prev_hours + 1):
        target_time = now - timedelta(hours=hours_ago)
        y, m, d, h = target_time.timetuple()[:4]
        prefix = f"{S3_BUCKET}/{y:04}/{m:02}/{d:02}/{site_id}/{site_id}{y:04}{m:02}{d:02}_{h:02}"
        file_paths = [f for f in fs.glob(f"{prefix}*") if "_MDM" not in f]
        if file_paths:
            paths[target_time] = f"s3://{sorted(file_paths)[0]}"

    return paths


@st.cache_data(ttl=3600, show_spinner=False)
def get_nexrad_radar(
    nexrad_file_path: str, fields: List[str] = [Fields.REFLECTIVITY.value]
) -> Radar:
    return pyart.io.read_nexrad_archive(nexrad_file_path, include_fields=fields)
