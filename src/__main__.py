import re
from collections import defaultdict
from typing import Optional, Tuple, Dict, List
from src.rules import CityRule, LowestSPriceRule, MonthlyCapRule, DiscountRule, FreeLargeRule, PopularPairDiscountRule
from src.config import PRICE_TABLE, MONTHLY_DISCOUNT_CAP, POPULAR_PAIRS_DISCOUNTS, BIG_CITIES, SMALL_CITIES, ALL_CITIES, Shipment
import sys
import json
import os
from datetime import datetime

# -----------------------------
# Vinted Shipping Discount System
# -----------------------------
# This script processes shipment records, applies pricing and discount rules,
# and outputs the final price, discount, and delivery time for each shipment.
# Rules are modular and extensible.
#
# Input format: YYYY-MM-DD SIZE PROVIDER ORIGIN DESTINATION
# Output format: <all fields> <final_price> <discount> <delivery_time>
# -----------------------------

# All config and constants are now in src/config.py


def parse_line(line: str) -> Optional[Shipment]:
    """
    Parses a line of input into a Shipment object, or returns None if invalid.
    """
    # Regex expects: YYYY-MM-DD SIZE PROVIDER ORIGIN DESTINATION
    pattern = r"^(\d{4}-\d{2}-\d{2})\s+(XS|S|M|L|XL)\s+(LP|MR)\s+(\w+)\s+(\w+)$"
    match = re.match(pattern, line.strip())
    if match:
        date, size, provider, origin, destination = match.groups()
        # Validate date
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return None
        return Shipment(date, size, provider, origin, destination)
    return None


def process_lines(lines: List[str]) -> List[str]:
    """
    Processes a list of input lines, applies all rules, and returns the output lines.
    """
    context: Dict = {}  # Shared state for rules (e.g., monthly discount tracking)
    rules: List[DiscountRule] = [
        CityRule(),         # Adjusts price and delivery time based on city types
        FreeLargeRule(),    # Every 3rd L and 4th XL via LP per month is free
        LowestSPriceRule(), # Ensures XS/S packages are charged at the lowest price (plus city adj.)
        PopularPairDiscountRule(), # Special discount for popular city pairs
        MonthlyCapRule(),   # Caps total monthly discounts
    ]
    output: List[str] = []
    for line in lines:
        shipment = parse_line(line)
        if shipment and not shipment.ignored:
            for rule in rules:
                rule.apply(shipment, context)  # Apply each rule in order
            if not shipment.ignored:
                output.append(shipment.output_line())  # Output formatted shipment
            else:
                output.append(f"{line.strip()} Ignored")  # Mark ignored if set by a rule
        else:
            output.append(f"{line.strip()} Ignored")  # Mark ignored if parsing failed
    return output


def main() -> None:
    """
    Main entry point: reads input file, processes lines, and prints results.
    """
    # Use command-line argument for input file, or default path
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'D:/Proga/Projects_my/Vinted_asignment/input.txt'
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        results = process_lines(lines)
        for line in results:
            print(line)
    except FileNotFoundError:
        print(f"Input file '{input_file}' not found.")

if __name__ == '__main__':
    main() 