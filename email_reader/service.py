from typing import List
from models import CamsWBR2, CamsWBR9
from repository import GenericRepository, sqlalchemy_to_dict

def calculate_current_nav(current_val, units):
    if units == 0:
        return 0
    return current_val / units

def inv_cal(transaction_type, amount):
    if transaction_type.startswith(('P', 'SI', 'TI', 'DR')):
        return amount
    return 0

def red_cal(transaction_type, units):
    if transaction_type.startswith(('R', 'SO', 'TO')):
        return -units
    return 0

def calculate_values(data, current_val, current_units):
    invested_amount = 0
    redeemed_units = 0
    sold_units = 0
    inv_left = 0
    adjusted_units = 0
    adjusted_amount = 0
    adjusted_nav = 0

    trade_dates = []
    transaction_types = []
    amounts = []
    units = []
    navs = []

    for record in data:
        trade_dates.append(record.TRADDATE)
        transaction_types.append(record.TRXNTYPE)
        amounts.append(record.AMOUNT)
        units.append(record.UNITS)
        navs.append(record.PURPRICE)

    for trx_type, amount in zip(transaction_types, amounts):
        invested_amount += inv_cal(trx_type, amount)

    for trx_type, unit in zip(transaction_types, units):
        redeemed_units += red_cal(trx_type, unit)

    sold_units = 0
    inv_left = invested_amount

    for trx_type, amount, unit, nav in zip(transaction_types, amounts, units, navs):
        if sold_units == redeemed_units or unit is None:
            break
        elif sold_units > redeemed_units:
            adjusted_units = sold_units - redeemed_units
            adjusted_amount = adjusted_units * navs[-1]
            inv_left -= adjusted_amount
            adjusted_nav = navs[-1]
            break
        elif trx_type.startswith(('P', 'SI', 'TI', 'DR')):
            inv_left -= amount
            sold_units += unit

    return {
        "Invested Amount": invested_amount,
        "Investment Left": inv_left,
        "Unrealized Gain/Loss": current_val - inv_left,
        "Current NAV": calculate_current_nav(current_val, current_units),
        "Redeemed Units": redeemed_units,
        "Sold Units": sold_units,
        "Adjusted Units": adjusted_units,
        "Adjusted Amount": adjusted_amount,
        "Adjusted NAV": adjusted_nav
    }

def get_user_data(pan_no: str = None):
    filters = {}
    if pan_no:
        filters["PAN_NO"] = pan_no

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
