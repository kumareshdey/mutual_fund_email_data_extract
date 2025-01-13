from collections import defaultdict
from typing import List
from models import CamsWBR2, CamsWBR9
from repository import GenericRepository, sqlalchemy_to_dict
from mapper import COLUMN_MAPPING

def calculate_current_nav(current_val, units):
    return current_val / units if units else 0

def inv_cal(transaction_type, amount):
    return amount if transaction_type.startswith(('P', 'SI', 'TI', 'DR')) else 0

def red_unit_cal(transaction_type, units):
    return units if transaction_type.startswith(('R', 'SO', 'TO')) else 0

def red_amt_cal(transaction_type, amount):
    return amount if transaction_type.startswith(('R', 'SO', 'TO')) else 0

def calculate_values(data, current_val, current_units):
    invested_amount = sum(inv_cal(rec[COLUMN_MAPPING['TRXNTYPE']], rec[COLUMN_MAPPING['AMOUNT']]) for rec in data)
    redeemed_units = sum(red_unit_cal(rec[COLUMN_MAPPING['TRXNTYPE']], rec[COLUMN_MAPPING['UNITS']]) for rec in data)
    redeemed_amount = sum(red_amt_cal(rec[COLUMN_MAPPING['TRXNTYPE']], rec[COLUMN_MAPPING['AMOUNT']]) for rec in data)

    sold_units = 0
    total_cost = 0
    ad_inv_left = redeemed_amount
    adjusted_units = 0
    adjusted_amount = 0
    adjusted_nav = 0

    for record in data:
        trx_type = record[COLUMN_MAPPING['TRXNTYPE']]
        amount = record[COLUMN_MAPPING['AMOUNT']]
        units = record[COLUMN_MAPPING['UNITS']]
        nav = record[COLUMN_MAPPING['PURPRICE']]

        if sold_units == redeemed_units or units is None:
            break

        if sold_units > redeemed_units:
            adjusted_units = sold_units - redeemed_units
            adjusted_amount = adjusted_units * nav
            ad_inv_left += adjusted_amount
            total_cost -= adjusted_amount
            adjusted_nav = nav
            break

        if trx_type.startswith(('P', 'SI', 'TI', 'DR')):
            sold_units += units
            cost = units * nav
            ad_inv_left -= cost
            total_cost += cost

    investment_left = invested_amount - total_cost
    unreal_gain_loss = current_val - investment_left
    abs_return_percent = (current_val / investment_left) * 100 if investment_left else 0

    return {
        "Invested Amount": invested_amount,
        "Redeemed Amount": redeemed_amount,
        "Redeemed Units": redeemed_units,
        "Investment Left": investment_left,
        "Unrealized Gain/Loss": unreal_gain_loss,
        "Current NAV": calculate_current_nav(current_val, current_units),
        "Adjusted Units": adjusted_units,
        "Adjusted Amount": adjusted_amount,
        "Adjusted NAV": adjusted_nav,
        "Sold Units": sold_units,
        "Total Cost": total_cost,
        "Absolute Return Percent": abs_return_percent
    }

def get_user_data(pan_no: str = None):
    filters = {"PAN_NO": pan_no} if pan_no else {}
    filters['FOLIOCHK'] = "13299340/20"
    repository = GenericRepository()
    cams_wbr9: List[CamsWBR9] = repository.filter(CamsWBR9, **filters)
    cams_wbr9_serialised_data = sqlalchemy_to_dict(cams_wbr9)

    modified_data = []
    for i, x in enumerate(cams_wbr9):
        cams_wbr2_data: List[CamsWBR2] = x.CAMS_WBR2_DATA
        cams_wbr9_serialised_data[i]["CAMS_WBR2_DATA"] = [sqlalchemy_to_dict(y) for y in cams_wbr2_data]

        wbr2_dict = defaultdict(list)
        for y in cams_wbr9_serialised_data[i]["CAMS_WBR2_DATA"]:
            wbr2_dict[y[COLUMN_MAPPING["SCHEME"]]].append(y)

        for key, val in wbr2_dict.items():
            z = cams_wbr9_serialised_data[i].copy()
            z["CAMS_WBR2_DATA"] = val
            modified_data.append(z)

    serialised_data = modified_data

    for i, x in enumerate(serialised_data):
        cams_wbr2_data = x.get("CAMS_WBR2_DATA", [])
        if not cams_wbr2_data:
            continue

        calculated_values = calculate_values(
            cams_wbr2_data, 
            x[COLUMN_MAPPING["RUPEE_BAL"]], 
            x[COLUMN_MAPPING["CLOS_BAL"]]
        )
        serialised_data[i].update(calculated_values)

    return serialised_data

if __name__ == '__main__':
    print(get_user_data())
