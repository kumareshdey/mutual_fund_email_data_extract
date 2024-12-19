from typing import List
from models import CamsWBR2, CamsWBR9
from repository import GenericRepository, sqlalchemy_to_dict
from mapper import COLUMN_MAPPING

def calculate_current_nav(current_val, units):
    if units == 0:
        return 0
    return current_val/units

def calculate_invested_amount(trade_dates, transaction_types, amounts):
    invested_amount = 0
    for i, trx_type in enumerate(transaction_types):
        if trx_type.startswith("P"):  # Purchase
            invested_amount += amounts[i]
        elif trx_type.startswith("R"):  # Redemption
            invested_amount -= amounts[i]
        elif trx_type.startswith("S") and trx_type[1] == "I":  # Switch-In
            invested_amount += amounts[i]
        elif trx_type.startswith("S") and trx_type[1] == "O":  # Switch-Out
            invested_amount -= amounts[i]
        elif trx_type.startswith("T") and trx_type[1] == "I":  # Transfer-In
            invested_amount += amounts[i]
        elif trx_type.startswith("T") and trx_type[1] == "O":  # Transfer-Out
            invested_amount -= amounts[i]
        elif trx_type.startswith("D") and trx_type[1] == "R":  # Dividend Reinvestment
            invested_amount += amounts[i]

    return invested_amount

def calculate_gain_loss(current_val, invested_amount):
    return current_val - invested_amount

def get_user_data(
        pan_no: str = None,
):
    filters = {}
    if pan_no:
        filters["PAN_NO"] = pan_no
    repository = GenericRepository()
    cams_wbr9: List[CamsWBR9] = repository.filter(CamsWBR9, **filters)
    serialised_data = sqlalchemy_to_dict(cams_wbr9)

    for i, x in enumerate(cams_wbr9):
        trade_dates = []
        transaction_types = []
        amounts = []

        for y in x.CAMS_WBR2_DATA:
            if serialised_data[i].get("CAMS_WBR2_DATA") is None:
                serialised_data[i]["CAMS_WBR2_DATA"] = []
            serialised_data[i]["CAMS_WBR2_DATA"].append(sqlalchemy_to_dict(y))
            trade_dates.append(y.TRADDATE)
            transaction_types.append(y.TRXNTYPE)
            amounts.append(y.AMOUNT)
        serialised_data[i]["Current NAV"] = calculate_current_nav(
            x.RUPEE_BAL, x.CLOS_BAL
        )

        serialised_data[i]["Invested Amount"] = calculate_invested_amount(
            trade_dates, transaction_types, amounts
        )

        serialised_data[i]["Gain Loss"] = calculate_gain_loss(
            x.RUPEE_BAL, serialised_data[i]["Invested Amount"]
        )

    return serialised_data

if __name__ == '__main__':
    print(get_user_data())
    
