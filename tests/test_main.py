import unittest
from shipments.__main__ import process_lines


class TestShipmentDiscounts(unittest.TestCase):
    def test_xs_and_s_lowest_price(self):
        lines = [
            '2015-02-01 XS MR Paris Lyon',  # MR XS: 1.20, LP XS: 1.00 (lowest)
            '2015-02-02 XS LP Paris Lyon',  # LP XS: 1.00 (lowest)
            '2015-02-03 S MR Paris Lyon',   # MR S: 2.00, LP S: 1.50 (lowest)
            '2015-02-04 S LP Paris Lyon',   # LP S: 1.50 (lowest)
        ]
        expected = [
            '2015-02-01 XS MR Paris Lyon 1.00 0.20 1-3 days',
            '2015-02-02 XS LP Paris Lyon 1.00 - 1-3 days',
            '2015-02-03 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-04 S LP Paris Lyon 1.00 0.50 1-3 days',
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_l_and_xl_free_rules(self):
        lines = [
            # L via LP: 3rd is free
            '2015-02-01 L LP Paris Lyon',
            '2015-02-02 L LP Paris Lyon',
            '2015-02-03 L LP Paris Lyon',  # free
            '2015-02-04 L LP Paris Lyon',
            # XL via LP: 4th is free
            '2015-02-01 XL LP Paris Lyon',
            '2015-02-02 XL LP Paris Lyon',
            '2015-02-03 XL LP Paris Lyon',
            '2015-02-04 XL LP Paris Lyon',  # free
            '2015-02-05 XL LP Paris Lyon',
        ]
        expected = [
            '2015-02-01 L LP Paris Lyon 6.90 - 1-3 days',
            '2015-02-02 L LP Paris Lyon 6.90 - 1-3 days',
            '2015-02-03 L LP Paris Lyon 0.00 6.90 1-3 days',
            '2015-02-04 L LP Paris Lyon 6.90 - 1-3 days',
            '2015-02-01 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-02-02 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-02-03 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-02-04 XL LP Paris Lyon 0.00 9.00 1-3 days',
            '2015-02-05 XL LP Paris Lyon 9.00 - 1-3 days',
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_popular_city_pair_discount(self):
        lines = [
            '2015-02-01 S MR Paris Lyon',      # popular pair, discount 0.5
            '2015-02-02 S MR Lyon Paris',      # popular pair, discount 0.5 (reverse)
            '2015-02-03 S MR Lyon Marseille',  # popular pair, discount 0.7
            '2015-02-04 S MR Paris Nice',      # popular pair, discount 1.0
            '2015-02-05 S MR Paris Dijon',     # not a popular pair
        ]
        expected = [
            '2015-02-01 S MR Paris Lyon 1.00 1.00 1-3 days',  # lowest S is 1.50, -0.5 = 1.00
            '2015-02-02 S MR Lyon Paris 1.00 1.00 1-3 days',
            '2015-02-03 S MR Lyon Marseille 0.80 1.20 1-3 days',
            '2015-02-04 S MR Paris Nice 0.50 1.50 1-3 days',
            '2015-02-05 S MR Paris Dijon 2.50 0.50 2-5 days',
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_monthly_cap_with_popular_pair(self):
        # 20 S MR Paris Lyon (popular pair, discount 1.00 each, cap is 10)
        lines = [f'2015-02-{i:02d} S MR Paris Lyon' for i in range(1, 22)]
        expected = [
            '2015-02-{:02d} S MR Paris Lyon 1.00 1.00 1-3 days'.format(i) for i in range(1, 11)
        ]
        expected += [
            '2015-02-{:02d} S MR Paris Lyon 2.00 - 1-3 days'.format(i) for i in range(11, 22)
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_invalid_and_edge_cases(self):
        lines = [
            '2015-02-01 XS MR Paris UnknownCity',  # unknown city
            '2015-02-02 S MR UnknownCity Lyon',    # unknown city
            '2015-02-03 S MR Paris Lyon',          # valid
            'bad input',                           # invalid format
            '2015-02-04 XL LP Paris Lyon',         # XL, not 4th, not free
        ]
        expected = [
            '2015-02-01 XS MR Paris UnknownCity Ignored',
            '2015-02-02 S MR UnknownCity Lyon Ignored',
            '2015-02-03 S MR Paris Lyon 1.00 1.00 1-3 days',
            'bad input Ignored',
            '2015-02-04 XL LP Paris Lyon 9.00 - 1-3 days',
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_leap_year_and_invalid_dates(self):
        lines = [
            '2016-02-29 S MR Paris Lyon',  # valid leap day
            '2015-02-29 S MR Paris Lyon',  # invalid date (2015 not leap year)
            '2015-13-01 S MR Paris Lyon',  # invalid month
            '2015-00-10 S MR Paris Lyon',  # invalid month
            '2015-01-32 S MR Paris Lyon',  # invalid day
        ]
        expected = [
            '2016-02-29 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-29 S MR Paris Lyon Ignored',
            '2015-13-01 S MR Paris Lyon Ignored',
            '2015-00-10 S MR Paris Lyon Ignored',
            '2015-01-32 S MR Paris Lyon Ignored',
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_unknown_provider_and_size(self):
        lines = [
            '2015-02-01 S XX Paris Lyon',  # unknown provider
            '2015-02-01 Q MR Paris Lyon',  # unknown size
            '2015-02-01 Q XX Paris Lyon',  # both unknown
        ]
        expected = [
            '2015-02-01 S XX Paris Lyon Ignored',
            '2015-02-01 Q MR Paris Lyon Ignored',
            '2015-02-01 Q XX Paris Lyon Ignored',
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_empty_and_whitespace_lines(self):
        lines = [
            '',
            '   ',
            '\n',
        ]
        expected = [
            ' Ignored',
            ' Ignored',
            ' Ignored',
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_duplicate_free_l_and_xl_rules(self):
        lines = [
            # 3rd L via LP in two different months
            '2015-02-01 L LP Paris Lyon',
            '2015-02-02 L LP Paris Lyon',
            '2015-02-03 L LP Paris Lyon',  # free in Feb
            '2015-03-01 L LP Paris Lyon',
            '2015-03-02 L LP Paris Lyon',
            '2015-03-03 L LP Paris Lyon',  # free in Mar
            # 4th XL via LP in two different months
            '2015-02-01 XL LP Paris Lyon',
            '2015-02-02 XL LP Paris Lyon',
            '2015-02-03 XL LP Paris Lyon',
            '2015-02-04 XL LP Paris Lyon',  # free in Feb
            '2015-03-01 XL LP Paris Lyon',
            '2015-03-02 XL LP Paris Lyon',
            '2015-03-03 XL LP Paris Lyon',
            '2015-03-04 XL LP Paris Lyon',  # free in Mar
        ]
        expected = [
            '2015-02-01 L LP Paris Lyon 6.90 - 1-3 days',
            '2015-02-02 L LP Paris Lyon 6.90 - 1-3 days',
            '2015-02-03 L LP Paris Lyon 0.00 6.90 1-3 days',
            '2015-03-01 L LP Paris Lyon 6.90 - 1-3 days',
            '2015-03-02 L LP Paris Lyon 6.90 - 1-3 days',
            '2015-03-03 L LP Paris Lyon 0.00 6.90 1-3 days',
            '2015-02-01 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-02-02 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-02-03 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-02-04 XL LP Paris Lyon 0.00 9.00 1-3 days',
            '2015-03-01 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-03-02 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-03-03 XL LP Paris Lyon 9.00 - 1-3 days',
            '2015-03-04 XL LP Paris Lyon 0.00 9.00 1-3 days',
        ]
        self.assertEqual(process_lines(lines), expected)

    def test_monthly_cap_edge_case(self):
        # Cap is 10, last discount should be partial if needed
        lines = [
            '2015-02-01 S MR Paris Lyon',  # discount 1.00
            '2015-02-02 S MR Paris Lyon',  # discount 1.00
            '2015-02-03 S MR Paris Lyon',  # discount 1.00
            '2015-02-04 S MR Paris Lyon',  # discount 1.00
            '2015-02-05 S MR Paris Lyon',  # discount 1.00
            '2015-02-06 S MR Paris Lyon',  # discount 1.00
            '2015-02-07 S MR Paris Lyon',  # discount 1.00
            '2015-02-08 S MR Paris Lyon',  # discount 1.00
            '2015-02-09 S MR Paris Lyon',  # discount 1.00
            '2015-02-10 S MR Paris Lyon',  # discount 1.00 (cap reached)
            '2015-02-11 S MR Paris Lyon',  # no discount
        ]
        expected = [
            '2015-02-01 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-02 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-03 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-04 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-05 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-06 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-07 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-08 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-09 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-10 S MR Paris Lyon 1.00 1.00 1-3 days',
            '2015-02-11 S MR Paris Lyon 2.00 - 1-3 days',
        ]
        self.assertEqual(process_lines(lines), expected)

if __name__ == '__main__':
    unittest.main() 