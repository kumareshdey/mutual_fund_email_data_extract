from models import CamsWBR2, CamsWBR9
from repository import GenericRepository, sqlalchemy_to_dict


def get_user_data(
        pan_no: str = None,
        folio_no: str = None
):
    repository = GenericRepository()
    cams_wbr9 = repository.filter(CamsWBR9)
    serialised_data = sqlalchemy_to_dict(cams_wbr9)
    for i, x in enumerate(cams_wbr9):
        for y in x.CAMS_WBR2_DATA:
            if serialised_data[i].get('CAMS_WBR2_DATA') is None:
                serialised_data[i]['CAMS_WBR2_DATA'] = []
            serialised_data[i]['CAMS_WBR2_DATA'].append(sqlalchemy_to_dict(y))
    return serialised_data

if __name__ == '__main__':
    print(get_user_data())
    
