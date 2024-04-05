# _*_ coding: utf-8 _*_
#
# Copyright (C) 2024 - 2024 SepineTam, Inc. All Rights Reserved 
#
# @Time    : 2024/4/5 17:38
# @Author  : Sepine Tam
# @File_path = "test/test.py"
from models.account import *


def test():
    database = "test.db"
    cash = CurrentAsset(db_path=database, asset_type="cash", value=200)
    wechat = CurrentAsset(db_path=database, asset_type="wechat", value=20)
    alipay = CurrentAsset(db_path=database, asset_type="alipay", value=120)
    icbc = CurrentAsset(db_path=database, asset_type="icbc", value=90)
    stock_000002SZ = InvestmentAsset(db_path=database, asset_type="stock_000002SZ", value=2000)
    cash.add_deposit(-20, use="干饭")
    stock_000002SZ.add_deposit(4000)
