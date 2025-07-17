from collections import defaultdict
from typing import Dict, Set
from shipments.config import PRICE_TABLE, Shipment, MONTHLY_DISCOUNT_CAP, POPULAR_PAIRS_DISCOUNTS

class DiscountRule:
    """
    Base class for all discount and adjustment rules.
    """
    def apply(self, shipment: Shipment, context: dict) -> None:
        pass

class CityRule(DiscountRule):
    """
    Adjusts price and sets delivery time based on city types (big/small).
    """
    def apply(self, shipment: 'Shipment', context: dict) -> None:
        otype = shipment.origin_type
        dtype = shipment.destination_type
        if otype == 'unknown' or dtype == 'unknown':
            shipment.ignored = True  # Ignore if city is not recognized
            return
        # Price adjustment and delivery time
        if otype == 'big' and dtype == 'big':
            price_adj = 0
            shipment.delivery_time = '1-3 days'
        elif (otype == 'big' and dtype == 'small') or (otype == 'small' and dtype == 'big'):
            price_adj = 1
            shipment.delivery_time = '2-5 days'
        elif otype == 'small' and dtype == 'small':
            price_adj = 2
            shipment.delivery_time = '3-6 days'
        else:
            price_adj = 0
            shipment.delivery_time = '-'
        shipment.price += price_adj  # Adjust base price
        shipment.final_price += price_adj  # Adjust final price (may be overwritten by other rules)

class LowestSPriceRule(DiscountRule):
    """
    Ensures XS and S packages are charged at the lowest XS/S price (plus city adjustment).
    """
    def apply(self, shipment: 'Shipment', context: dict) -> None:
        if shipment.is_free:
            return
        if shipment.size in ('XS', 'S'):
            # Calculate city adjustment for this shipment
            otype = shipment.origin_type
            dtype = shipment.destination_type
            if otype == 'big' and dtype == 'big':
                city_adj = 0
            elif (otype == 'big' and dtype == 'small') or (otype == 'small' and dtype == 'big'):
                city_adj = 1
            elif otype == 'small' and dtype == 'small':
                city_adj = 2
            else:
                city_adj = 0
            # Find the lowest price for this size among all providers, then add city adjustment
            lowest_size_with_city = min(PRICE_TABLE[provider][shipment.size] for provider in PRICE_TABLE) + city_adj
            shipment.discount = shipment.price - lowest_size_with_city
            shipment.final_price = lowest_size_with_city
            shipment.lowest_price_applied = True

class FreeLargeRule(DiscountRule):
    """
    Every 3rd L package via LP per month is free (once per month).
    Every 4th XL package via LP per month is free (once per month).
    """
    def apply(self, shipment: 'Shipment', context: dict) -> None:
        if shipment.is_free:
            return
        if shipment.provider == 'LP':
            # L logic: every 3rd L per month
            if shipment.size == 'L':
                l_lp_count: Dict = context.setdefault('l_lp_count', defaultdict(int))
                l_lp_discount_given: Set = context.setdefault('l_lp_discount_given', set())
                l_lp_count[shipment.year_month] += 1
                if l_lp_count[shipment.year_month] == 3 and shipment.year_month not in l_lp_discount_given:
                    shipment.discount = shipment.price
                    shipment.final_price = 0.0
                    shipment.is_free = True
                    l_lp_discount_given.add(shipment.year_month)
            # XL logic: every 4th XL per month
            elif shipment.size == 'XL':
                xl_lp_count: Dict = context.setdefault('xl_lp_count', defaultdict(int))
                xl_lp_discount_given: Set = context.setdefault('xl_lp_discount_given', set())
                xl_lp_count[shipment.year_month] += 1
                if xl_lp_count[shipment.year_month] == 4 and shipment.year_month not in xl_lp_discount_given:
                    shipment.discount = shipment.price
                    shipment.final_price = 0.0
                    shipment.is_free = True
                    xl_lp_discount_given.add(shipment.year_month)

class MonthlyCapRule(DiscountRule):
    """
    Caps total monthly discounts at a fixed amount (e.g., 10 EUR).
    """
    def apply(self, shipment: 'Shipment', context: dict) -> None:
        if shipment.is_free:
            shipment.final_price = 0.0
            shipment.discount = shipment.price
            shipment.discount_str = f"{shipment.discount:.2f}"
            return
        # Track total discount given per month
        monthly_discount: Dict = context.setdefault('monthly_discount', defaultdict(float))
        available = MONTHLY_DISCOUNT_CAP - monthly_discount[shipment.year_month]
        if available <= 0:
            # Cap reached, no discount, revert to original price and exit
            shipment.final_price = shipment.price
            shipment.discount = 0.0
            shipment.discount_str = '-'
            return
        if shipment.discount > 0:
            if shipment.discount > available:
                # Partial discount if not enough cap left
                shipment.discount = available
                shipment.final_price = shipment.price - shipment.discount
                monthly_discount[shipment.year_month] += shipment.discount
                shipment.discount_str = f"{shipment.discount:.2f}"
            else:
                # Full discount
                shipment.final_price = shipment.price - shipment.discount
                monthly_discount[shipment.year_month] += shipment.discount
                shipment.discount_str = f"{shipment.discount:.2f}"
        else:
            # No discount
            shipment.final_price = shipment.price
            shipment.discount = 0.0
            shipment.discount_str = '-'

class PopularPairDiscountRule(DiscountRule):
    """
    Applies a special discount if the shipment is between a popular city pair.
    Only applies to S shipments (not XS, M, L, XL).
    """
    def apply(self, shipment: 'Shipment', context: dict) -> None:
        if shipment.is_free:
            return
        if shipment.size != 'S':
            return
        pair = (shipment.origin, shipment.destination)
        pair_rev = (shipment.destination, shipment.origin)
        discount = None
        if pair in POPULAR_PAIRS_DISCOUNTS:
            discount = POPULAR_PAIRS_DISCOUNTS[pair]
        elif pair_rev in POPULAR_PAIRS_DISCOUNTS:
            discount = POPULAR_PAIRS_DISCOUNTS[pair_rev]
        if discount is not None and discount > 0:
            # Only apply if discount is less than the current price
            shipment.discount += min(discount, shipment.final_price)
            shipment.final_price = max(0.0, shipment.final_price - discount)
            # Note: discount_str will be set by MonthlyCapRule 