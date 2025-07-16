import json
import os
from typing import Dict, Tuple, Set

# Load city definitions from config file
CITIES_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../cities.json')
with open(CITIES_CONFIG_PATH, 'r') as f:
    cities_data = json.load(f)
BIG_CITIES: Set[str] = set(cities_data['big'])
SMALL_CITIES: Set[str] = set(cities_data['small'])
ALL_CITIES: Set[str] = BIG_CITIES | SMALL_CITIES

# Price table: provider -> size -> price
PRICE_TABLE: Dict[str, Dict[str, float]] = {
    'LP': {'XS': 1.00, 'S': 1.50, 'M': 4.90, 'L': 6.90, 'XL': 9.00},
    'MR': {'XS': 1.20, 'S': 2.00, 'M': 3.00, 'L': 4.00, 'XL': 7.00},
}

# Maximum total discount allowed per month
MONTHLY_DISCOUNT_CAP: float = 10.0

# Special discounts for popular city pairs
POPULAR_PAIRS_DISCOUNTS: Dict[Tuple[str, str], float] = {
    ('Paris', 'Lyon'): 0.5,
    ('Lyon', 'Paris'): 0.5,
    ('Lyon', 'Marseille'): 0.7,
    ('Paris', 'Nice'): 1.0,
    # ...add both (A, B) and (B, A) for bidirectional
}

class Shipment:
    """
    Represents a single shipment record, including all fields needed for pricing and discount rules.
    """
    def __init__(self, date: str, size: str, provider: str, origin: str, destination: str):
        self.date: str = date
        self.size: str = size
        self.provider: str = provider
        self.origin: str = origin
        self.destination: str = destination
        self.price: float = PRICE_TABLE[provider][size]  # Base price before any rules
        self.final_price: float = self.price  # Will be adjusted by rules
        self.discount: float = 0.0
        self.discount_str: str = '-'
        # Extract year and month for monthly rules
        yyyy, mm, *_ = date.split('-')
        self.year_month: Tuple[str, str] = (yyyy, mm)  # (YYYY, MM)
        self.ignored: bool = False  # Set to True if the shipment should be ignored
        self.origin_type: str = self.city_type(origin)  # 'big', 'small', or 'unknown'
        self.destination_type: str = self.city_type(destination)
        self.delivery_time: str = '-'  # Will be set by CityRule
        self.is_free: bool = False  # Set to True if shipment is made free by a rule
        self.lowest_price_applied: bool = False  # Set to True if lowest XS/S price rule applied

    @staticmethod
    def city_type(city: str) -> str:
        """
        Returns 'big', 'small', or 'unknown' for a given city name.
        """
        if city in BIG_CITIES:
            return 'big'
        elif city in SMALL_CITIES:
            return 'small'
        else:
            return 'unknown'

    def output_line(self) -> str:
        """
        Formats the shipment's output line for display or file output.
        """
        return f"{self.date} {self.size} {self.provider} {self.origin} {self.destination} {self.final_price:.2f} {self.discount_str} {self.delivery_time}" 