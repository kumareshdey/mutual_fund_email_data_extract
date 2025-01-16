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

def calculate_values(data: List[CamsWBR2], current_val, current_units):
    invested_amount = sum(inv_cal(rec.TRXNTYPE, rec.AMOUNT) for rec in data)
    redeemed_units = sum(red_unit_cal(rec.TRXNTYPE, rec.UNITS) for rec in data)
    redeemed_amount = sum(red_amt_cal(rec.TRXNTYPE, rec.AMOUNT) for rec in data)

    sold_units = 0
    total_cost = 0
    ad_inv_left = redeemed_amount
    adjusted_units = 0
    adjusted_amount = 0
    adjusted_nav = 0

    for record in data:
        trx_type = record.TRXNTYPE
        amount = record.AMOUNT
        units = record.UNITS
        nav = record.PURPRICE

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

    # Additional calculations
    investment_left = invested_amount - total_cost
    unreal_gain_loss = current_val - investment_left
    unreal_gain_loss_percent = (unreal_gain_loss / investment_left) * 100 if investment_left else 0

    real_gain_loss = redeemed_amount - total_cost
    real_gain_loss_percent = (real_gain_loss / total_cost) * 100 if total_cost else 0

    abs_return_percent = (current_val / investment_left) * 100 if investment_left else 0

    return {
        "Invested Amount": invested_amount,
        "Redeemed Amount": redeemed_amount,
        "Redeemed Units": redeemed_units,
        "Investment Left": investment_left,
        "Unrealized Gain/Loss": unreal_gain_loss,
        "Unrealized Gain/Loss Percent": unreal_gain_loss_percent,
        "Realized Gain/Loss": real_gain_loss,
        "Realized Gain/Loss Percent": real_gain_loss_percent,
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
    repository = GenericRepository()
    cams_wbr9: List[CamsWBR9] = repository.filter(CamsWBR9, **filters)
    serialised_data = sqlalchemy_to_dict(cams_wbr9)

    for i, x in enumerate(cams_wbr9):
        cams_wbr2_data = x.CAMS_WBR2_DATA
        if not cams_wbr2_data:
            continue
        serialised_data[i]["CAMS_WBR2_DATA"] = [sqlalchemy_to_dict(y) for y in cams_wbr2_data]
        calculated_values = calculate_values(cams_wbr2_data, x.RUPEE_BAL, x.CLOS_BAL)
        serialised_data[i].update(calculated_values)

    return serialised_data

if __name__ == '__main__':
    print(get_user_data())
