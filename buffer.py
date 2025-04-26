import threading
from collections import defaultdict, deque
from datetime import datetime, timezone

import streamlit as st
from cachetools import LRUCache

from fields import Fields
from nexrad import get_hourly_nexrad_file_paths, get_nexrad_radar
from reflectivity import nexrad_radar_to_reflectivity_snapshot


class NEXRADReflectivitySnapshotBuffer:
    def __init__(
        self,
        max_sites: int = 5,
        max_snapshots: int = 3,
    ):
        self.buffer_lock = threading.Lock()
        self.size = max_snapshots
        self.last_updates = defaultdict(lambda: datetime.min.replace(tzinfo=timezone.utc))
        self.site_buffers = LRUCache(maxsize=max_sites)

    def add_data(self, site_id: str = "KSOX", prev_hours: int = 3):
        last_update = self.last_updates[site_id]
        nexrad_file_paths = get_hourly_nexrad_file_paths(site_id=site_id, prev_hours=prev_hours)
        if not nexrad_file_paths:
            return

        for target_time, fp in sorted(nexrad_file_paths.items()):
            if target_time <= last_update:
                continue

            radar = get_nexrad_radar(fp, fields=[Fields.REFLECTIVITY.value])  # streamlit cached
            snapshot = nexrad_radar_to_reflectivity_snapshot(target_time, site_id, radar, -20.0, 20)
            with self.buffer_lock:
                self.site_buffers[site_id].appendleft(snapshot)
                last_update = target_time
        self.last_updates[site_id] = last_update

    def get_snapshots(self, site_id: str = "KSOX"):
        self.update_buffer(site_id)
        st.write(f"Cached sites: {list(self.site_buffers.keys())}")
        return list(self.site_buffers[site_id])

    def update_buffer(self, site_id):
        if site_id not in self.site_buffers:
            self.site_buffers[site_id] = deque(maxlen=self.size)
            self.add_data(site_id, self.size)
        elif len(self.site_buffers[site_id]) < self.size:
            self.add_data(site_id, self.size - len(self.site_buffers[site_id]))
