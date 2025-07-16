# Vinted Shipping Discount System

## Overview

This project implements a flexible shipping price and discount calculation system for Vinted, supporting multiple providers, package sizes, and a variety of discount rules. The system is designed for easy extension and modification of rules.

---

## Basic Features (from the original assignment)

1. **Lowest S/XS Price Rule**  
   - All S and XS shipments are always charged at the lowest available price among providers (plus any city adjustment).

2. **Free L/XL Shipments via LP**  
   - Every 3rd L and every 4th XL shipment via LP is free, but only once per calendar month.

3. **Monthly Discount Cap**  
   - The total amount of discounts given in a calendar month cannot exceed 10 €. If the cap is reached, further discounts are not applied, or are partially applied if the cap is nearly reached.

4. **Input/Output Format**  
   - Input: Each line in `input.txt` contains `YYYY-MM-DD SIZE PROVIDER ORIGIN DESTINATION`.
   - Output: Each line includes the original input, the final price, the discount applied (or `-` if none), and the delivery time. Invalid or unrecognized lines are marked as `Ignored`.

---

## Additional Features

1. **City-Based Pricing and Delivery Time**
   - Cities are classified as 'big' or 'small' (see `cities.json`).
   - Price and delivery time are adjusted based on the origin and destination city types:
     - big→big, big→small, small→big, small→small, and unknown city cases are all handled.

2. **Popular City Pair Discounts**
   - Special discounts are applied for S shipments between certain popular city pairs (see `src/config.py`).

3. **Support for More Package Sizes**
   - In addition to S, M, L, the system supports XS and XL sizes.

4. **Flexible Rule System**
   - All rules are implemented as modular classes, making it easy to add, remove, or modify rules.

5. **Comprehensive Error Handling**
   - Lines with unknown cities, invalid formats, unrecognized providers/sizes, or invalid calendar dates are marked as `Ignored`.

6. **Delivery Time Calculation**
   - Delivery time is included in the output and is based on city types.

7. **Date Validation**
   - The system validates that all dates are real calendar dates (e.g., 2015-02-29 is invalid and will be marked as `Ignored`).

---

## How to Run

### **Run the Solution**

From the project root, run:
```bash
python -m src.__main__
```
- By default, this reads from `input.txt` in the project root.
- Output is printed to the console.

### **Run the Tests**

From the project root, run:
```bash
python -m unittest discover
```
- All tests are located in the `tests/` directory.

---

## Project Structure

```
Vinted_asignment/
  src/
    __main__.py      # Main entry point
    rules.py         # All discount and pricing rules
    config.py        # Configuration: prices, cities, popular pairs
  tests/
    test_main.py     # Unit tests
  input.txt          # Input file for shipments
  cities.json        # City classification
  requirements.txt   # Python dependencies
```

---

## Extending the System

To add or modify rules, edit or add classes in `src/rules.py` and register them in the rules list in `src/__main__.py`. 