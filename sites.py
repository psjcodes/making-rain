import csv
from dataclasses import dataclass

from config import SITES_CSV

radar_sites = []


@dataclass(frozen=True)
class RadarSite:
    id: str
    city: str
    state: str
    lat: float
    lon: float
    alt: float


with open(SITES_CSV, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        site = RadarSite(
            id=row["id"],
            city=row["city"],
            state=row["state"],
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            alt=float(row["alt"]),
        )
        radar_sites.append(site)
