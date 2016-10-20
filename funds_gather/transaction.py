
class Account(object):
    def __init__(self, name, account_number):
        self.name = name
        self.account_number = account_number

class Fund(object):
    def __init__(self, name, ticker, cusip):
        self.name = name
        self.ticker = ticker
        self.cusip = cusip

    def __hash__(self):
        """ Provide this for hashing in sets"""
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, Fund):
            return(repr(self) == repr(other))

    def __repr__(self):
        return "Fund(%s, %s, %s)" % (self.name, self.ticker, self.cusip)

class Transaction(object):
    def __init__(self, fund, trans_date, trans_type, unit_price, units, invest_amount, account):
        self.date = trans_date
        self.fund = fund
        self.trans_type = trans_type
        self.unit_price = float(unit_price)
        self.units = float(units)
        self.invest_amount = float(invest_amount)
        self.account = account

    def __str__(self):
        return '%s %s - %s:  %s @ $%s (total $%s)' % (self.date, self.trans_type, self.fund.name, self.units, self.unit_price, self.invest_amount)
