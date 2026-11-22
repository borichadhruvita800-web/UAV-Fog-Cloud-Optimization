"""
Global project settings and topology definitions for UAV Fog-Cloud Optimization.
"""

from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
SCENARIOS_DIR = DATA_DIR / "scenarios"
RESULTS_DIR = DATA_DIR / "results"
TESTS_DIR = BASE_DIR / "tests"

BACKGROUND_IMAGE_PATH = ASSETS_DIR / "drone_sunset.jpg"

# Ensure runtime directories exist
SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Visual Design Theme (Drone Sunset Twilight Aerospace Operations Center)
THEME_CONFIG = {
    "background_color": "#0a0e1a",
    "surface_color": "rgba(16, 22, 38, 0.78)",
    "surface_border": "rgba(255, 167, 38, 0.28)",
    "accent_orange": "#ff7b00",
    "accent_amber": "#f59e0b",
    "accent_gold": "#fbbf24",
    "accent_sun": "#fde047",
    "accent_cyan": "#38bdf8",
    "accent_green": "#10b981",
    "accent_red": "#ef4444",
    "text_primary": "#f8fafc",
    "text_secondary": "#cbd5e1",
    "text_muted": "#94a3b8",
    "font_family": "Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif"
}

# Euro 28 Topology Nodes: 28 Cities with approximate geographic coordinates (Lat, Lon)
EURO_28_CITIES: Dict[str, Dict[str, float]] = {
    "London": {"lat": 51.5074, "lon": -0.1278, "country": "UK"},
    "Glasgow": {"lat": 55.8642, "lon": -4.2518, "country": "UK"},
    "Dublin": {"lat": 53.3498, "lon": -6.2603, "country": "Ireland"},
    "Amsterdam": {"lat": 52.3676, "lon": 4.9041, "country": "Netherlands"},
    "Brussels": {"lat": 50.8503, "lon": 4.3517, "country": "Belgium"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "country": "France"},
    "Lyon": {"lat": 45.7640, "lon": 4.8357, "country": "France"},
    "Bordeaux": {"lat": 44.8378, "lon": -0.5792, "country": "France"},
    "Strasbourg": {"lat": 48.5734, "lon": 7.7521, "country": "France"},
    "Madrid": {"lat": 40.4168, "lon": -3.7038, "country": "Spain"},
    "Barcelona": {"lat": 41.3879, "lon": 2.1699, "country": "Spain"},
    "Frankfurt": {"lat": 50.1109, "lon": 8.6821, "country": "Germany"},
    "Hamburg": {"lat": 53.5511, "lon": 9.9937, "country": "Germany"},
    "Berlin": {"lat": 52.5200, "lon": 13.4050, "country": "Germany"},
    "Munich": {"lat": 48.1351, "lon": 11.5820, "country": "Germany"},
    "Zurich": {"lat": 47.3769, "lon": 8.5417, "country": "Switzerland"},
    "Milan": {"lat": 45.4642, "lon": 9.1900, "country": "Italy"},
    "Rome": {"lat": 41.9028, "lon": 12.4964, "country": "Italy"},
    "Vienna": {"lat": 48.2082, "lon": 16.3738, "country": "Austria"},
    "Prague": {"lat": 50.0755, "lon": 14.4378, "country": "Czech Republic"},
    "Warsaw": {"lat": 52.2297, "lon": 21.0122, "country": "Poland"},
    "Budapest": {"lat": 47.4979, "lon": 19.0402, "country": "Hungary"},
    "Zagreb": {"lat": 45.8150, "lon": 15.9819, "country": "Croatia"},
    "Belgrade": {"lat": 44.7866, "lon": 20.4489, "country": "Serbia"},
    "Athens": {"lat": 37.9838, "lon": 23.7275, "country": "Greece"},
    "Copenhagen": {"lat": 55.6761, "lon": 12.5683, "country": "Denmark"},
    "Oslo": {"lat": 59.9139, "lon": 10.7522, "country": "Norway"},
    "Stockholm": {"lat": 59.3293, "lon": 18.0686, "country": "Sweden"},
}

# Default Cloud server location is Frankfurt (central telecommunication hub of Euro-28)
DEFAULT_CLOUD_CITY = "Frankfurt"

# Bidirectional optical links modeling Euro 28 topology (62 bidirectional links, ~600 km span each)
EURO_28_LINKS: List[Tuple[str, str]] = [
    ("Dublin", "Glasgow"),
    ("Dublin", "London"),
    ("Glasgow", "London"),
    ("London", "Amsterdam"),
    ("London", "Paris"),
    ("London", "Brussels"),
    ("Amsterdam", "Brussels"),
    ("Amsterdam", "Hamburg"),
    ("Amsterdam", "Frankfurt"),
    ("Brussels", "Paris"),
    ("Brussels", "Strasbourg"),
    ("Brussels", "Frankfurt"),
    ("Paris", "Bordeaux"),
    ("Paris", "Lyon"),
    ("Paris", "Strasbourg"),
    ("Bordeaux", "Madrid"),
    ("Madrid", "Barcelona"),
    ("Barcelona", "Lyon"),
    ("Lyon", "Zurich"),
    ("Lyon", "Milan"),
    ("Strasbourg", "Frankfurt"),
    ("Strasbourg", "Zurich"),
    ("Frankfurt", "Hamburg"),
    ("Frankfurt", "Berlin"),
    ("Frankfurt", "Munich"),
    ("Hamburg", "Berlin"),
    ("Hamburg", "Copenhagen"),
    ("Berlin", "Warsaw"),
    ("Berlin", "Prague"),
    ("Copenhagen", "Oslo"),
    ("Copenhagen", "Stockholm"),
    ("Oslo", "Stockholm"),
    ("Warsaw", "Prague"),
    ("Warsaw", "Budapest"),
    ("Prague", "Munich"),
    ("Prague", "Vienna"),
    ("Munich", "Zurich"),
    ("Munich", "Vienna"),
    ("Zurich", "Milan"),
    ("Milan", "Rome"),
    ("Rome", "Zagreb"),
    ("Vienna", "Budapest"),
    ("Vienna", "Zagreb"),
    ("Budapest", "Belgrade"),
    ("Zagreb", "Belgrade"),
    ("Belgrade", "Athens"),
    ("Rome", "Athens"),
]
