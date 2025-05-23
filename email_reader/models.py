from sqlalchemy import BigInteger, Column, ForeignKeyConstraint, Numeric, String, Integer, Float, Date, Boolean, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from db_connection import Base, engine

class CamsWBR2(Base):
    __tablename__ = "CAMS_WBR2"

    FOLIO_NO = Column(String, nullable=False)
    SCHEME = Column(String, nullable=False)
    BROKCODE = Column(String, nullable=True)
    SUBBROK = Column(String, nullable=True)
    PAN = Column(String, nullable=True)
    INV_NAME = Column(String, nullable=True)
    AMC_CODE = Column(String, nullable=True)
    PRODCODE = Column(String, nullable=True)
    SCHEME_TYP = Column(String, nullable=True)
    REP_DATE = Column(Date, nullable=True)
    USERCODE = Column(String, nullable=True)
    TRADDATE = Column(Date, nullable=True)
    POSTDATE = Column(Date, nullable=True)
    PURPRICE = Column(Numeric, nullable=True)
    UNITS = Column(Numeric, nullable=True)
    AMOUNT = Column(Numeric, nullable=True)
    STAMP_DUTY = Column(Numeric, nullable=True)
    TRXNNO = Column(String, nullable=True, primary_key=True, unique=True)
    USRTRXNO = Column(String, nullable=True)
    TRXN_NATUR = Column(String, nullable=True)
    TRXNTYPE = Column(String, nullable=True)
    TRXN_SUFFI = Column(String, nullable=True)
    SEQ_NO = Column(BigInteger, nullable=True)
    SIPTRXNNO = Column(String, nullable=True)
    SYS_REGN_D = Column(Date, nullable=True)
    CAMS_WBR9_DATA = relationship(
        "CamsWBR9",
        back_populates="CAMS_WBR2_DATA",
        lazy="selectin",
        primaryjoin=(
            "and_(CamsWBR9.FOLIOCHK == CamsWBR2.FOLIO_NO, "
            "CamsWBR9.SCH_NAME == CamsWBR2.SCHEME)"
        ),
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ["FOLIO_NO", "SCHEME"],  # Composite key in CAMS_WBR2
            ["CAMS_WBR9.FOLIOCHK", "CAMS_WBR9.SCH_NAME"],  # Composite key in CAMS_WBR9
        ),
    )


class CamsWBR9(Base):
    __tablename__ = "CAMS_WBR9"

    FOLIOCHK = Column(String, nullable=False)
    PAN_NO = Column(String, nullable=False)
    HOLDING_NA = Column(String, nullable=True)
    CLOS_BAL = Column(Numeric, nullable=True)
    RUPEE_BAL = Column(Numeric, nullable=True)
    EMAIL = Column(String, nullable=True)
    MOBILE_NO = Column(String, nullable=True)
    SCH_NAME = Column(String, nullable=False)
    CAMS_WBR2_DATA = relationship(
        "CamsWBR2",
        back_populates="CAMS_WBR9_DATA",
        lazy="selectin",
        primaryjoin=(
            "and_(CamsWBR9.FOLIOCHK == CamsWBR2.FOLIO_NO, "
            "CamsWBR9.SCH_NAME == CamsWBR2.SCHEME)"
        ),
    )

    __table_args__ = (
        PrimaryKeyConstraint("FOLIOCHK", "SCH_NAME", name="pk_foliochk_sch_name"),
    )
