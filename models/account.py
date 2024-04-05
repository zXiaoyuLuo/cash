# _*_ coding: utf-8 _*_
#
# Copyright (C) 2024 - 2024 SepineTam, Inc. All Rights Reserved
#
# @Time    : 2024/4/4 21:38
# @Author  : Sepine Tam
# @file_path = "models/account.py"

import sqlite3
from datetime import date


class CurrentDatabase:
    def __init__(self, conn, cur, asset_name):
        self.asset_name = asset_name
        self.conn = conn
        self.cur = cur
        self._make_table()

    def _make_table(self):
        sql = f"""CREATE TABLE IF NOT EXISTS {self.asset_name} (
        date TEXT NOT NULL,
        deposit REAL,
        use TEXT)"""
        self.cur.execute(sql)
        self.conn.commit()

    def add_item(self, day, deposit, use):
        sql = f"""INSERT INTO {self.asset_name} (date, deposit, use) VALUES (?, ?, ?)"""
        values = (day, deposit, use)
        self.cur.execute(sql, values)
        self.conn.commit()


class InvestmentCurrentDatabase:
    def __init__(self, conn, cur, asset_name):
        self.asset_name = asset_name
        self.conn = conn
        self.cur = cur
        self._make_table()

    def _make_table(self):
        sql = f"""CREATE TABLE IF NOT EXISTS {self.asset_name} (
        date TEXT NOT NULL,
        deposit INTEGER NOT NULL)"""
        self.cur.execute(sql)
        self.conn.commit()

    def add_item(self, day, deposit):
        sql = f"""INSERT INTO {self.asset_name} (date, deposit) VALUES (?, ?)"""
        values = (day, deposit)
        self.cur.execute(sql, values)
        self.conn.commit()


class Assets:
    def __init__(self, db_path, asset_name):
        self.db_path = db_path
        self.asset_name = asset_name
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.table_name = self.__class__.__name__
        if self.table_name == 'CurrentAsset':
            self._change_database = CurrentDatabase(self.conn, self.cur, asset_name)
        elif self.table_name == 'InvestmentAsset':
            self._change_database = InvestmentCurrentDatabase(self.conn, self.cur, asset_name)

    def note(self, day, deposit, use=None):
        """
        记录钱包发生的变化
        :param day: 变化的日期(默认为当天)
        :param deposit: 变动量
        :param use: 用途
        :return: None
        """
        if self.table_name == 'CurrentAsset':
            self._change_database.add_item(day, deposit, use)
        elif self.table_name == 'InvestmentAsset':
            self._change_database.add_item(day, deposit)

    def _make_table(self, sql):
        self.cur.execute(sql)
        self.conn.commit()

    def _make_item(self, sql, values):
        self.cur.execute(sql, values)
        self.conn.commit()

    def _account_exists(self, account) -> bool:
        """
        Check if account exists in the database
        :param account: 账户名称
        :return: 存在返回Ture，否则为False
        """
        sql_check = f"SELECT 1 FROM {self.table_name} WHERE account = ?"
        self.cur.execute(sql_check, (account,))
        return self.cur.fetchone() is not None

    def get_deposit(self):
        """
        获取当前的账户余额
        :return: 当前账户余额
        """
        sql = f"SELECT deposit FROM {self.table_name} WHERE account = ?"
        self.cur.execute(sql, (self.asset_name,))
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            return None

    def close(self):
        """
        关闭数据库连接
        :return: None
        """
        self.conn.close()


class CurrentAsset(Assets):
    def __init__(self, db_path: str, asset_type: str, value: float = 0):
        """
        初始化
        :param db_path: 数据库路径
        :param asset_type: 资产类别：现金(cash)、银行卡存款(card+账号)、微信(WeChat)、支付宝(Alipay)
        :param value: 账户初始金额
        """
        self.asset_name = asset_type
        self.table_name = self.__class__.__name__
        super().__init__(db_path=db_path, asset_name=self.asset_name)
        sql_table = f"""CREATE TABLE IF NOT EXISTS {self.table_name}(account TEXT, deposit REAL)"""
        self._make_table(sql_table)
        if not self._account_exists(self.asset_name):
            sql_load = f"""INSERT INTO {self.table_name} (account, deposit) VALUES (?, ?)"""
            self._make_item(sql_load, (self.asset_name, value))

    def add_deposit(self, amount: float, day: str = str(date.today()), use: str = "No"):
        """
        给当前账户增加金额
        :param amount: 增加的钱数
        :param day: 日期，默认为运行程序时的日期
        :param use: 用途
        :return: None
        """
        sql = """UPDATE CurrentAsset
                 SET deposit = deposit + ?
                 WHERE account = ?"""
        self.cur.execute(sql, (amount, self.asset_name))
        self.conn.commit()
        self.note(day=day, deposit=amount, use=use)


class InvestmentAsset(CurrentAsset):
    """
    初始化
    :param db_path: 数据路路径
    :param asset_type: 资产类别：股票(stock)、基金(fund)
    :param value: 持仓数量
    """

    def add_deposit(self, amount: int, day: str = str(date.today())):
        """
        当前投资类别的持仓变化
        :param amount: 变化数量
        :param day: 日期
        :return: None
        """
        sql = """UPDATE InvestmentAsset
                 SET deposit = deposit + ?
                 WHERE account = ?"""
        self.cur.execute(sql, (amount, self.asset_name))
        self.conn.commit()
        self.note(day=day, deposit=amount)

