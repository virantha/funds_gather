import requests
from lxml import html
import logging


class Transaction(object):
    def __init__(self, fund_id, trans_date, trans_type, unit_price, units, invest_amount):
        self.date = trans_date
        self.fund_id = fund_id
        self.trans_type = trans_type
        self.unit_price = float(unit_price)
        self.units = float(units)
        self.invest_amount = float(invest_amount)

    def __str__(self):
        return '%s - %s:  %s @ $%s (total $%s)' % (self.trans_type, self.fund_id, self.units, self.unit_price, self.invest_amount)

class MD529(object):

    urls = { 'home': 'https://secure.collegesavingsmd.org/pls/prod/twpkwbis.P_WWWLogin',
             'login': 'https://secure.collegesavingsmd.org/pls/prod/twpkwbis.P_ValLogin',
             'acct_summary': 'https://secure.collegesavingsmd.org/pls/prod/hwtkpage.P_HomePage',
             'acct_select': 'https://secure.collegesavingsmd.org/pls/prod/hwtkstmt.P_DispYearChoice',
             'transactions': 'https://secure.collegesavingsmd.org/pls/prod/hwtkstmt_MD.P_DispAcctStmt',
            }

    def __init__(self):
        self.session = requests.session()
        pass

    def login(self, user, password):
        authenticity_token = self.get_form_key(self.urls['home'])
        payload = { 'sid': user,
                    'PIN': password,
                    'VALSRCKEY': authenticity_token
                  }

        result = self.session.post( self.urls['login'],
                                        data = payload, 
                                        headers = dict(referer=self.urls['login'])
                                     )

    def get_accounts(self):
        url = self.urls['acct_select']
        logging.info("Accessing account information")
        result = self.session.get(
                url, 
                headers = dict(referer = url)
                )
        tree = html.fromstring(result.text)
        account_numbers = tree.xpath('//select[@name="cnum"]/option/@value')                                                                                                                                        
        return account_numbers


    def get_transactions(self, account, startdate=None):
        authenticity_token = self.get_form_key(self.urls['acct_select'])
        logging.info("Getting transactions for account %s" % account)
        logging.debug('Auth token %s' % authenticity_token)
        url = self.urls['transactions']
        payload = { 'cnum': account,
                    'trans': 'ALL',
                    'taxyear': '',
                    'fdate': '',
                    'tdate': '',
                    'callfrom': '',
                    'VALSRCKEY': authenticity_token
                    }
        result = self.session.post(
                    url, 
                    data = payload, 
                    headers = dict(referer=self.urls['acct_select'])
                )
        logging.debug(result.headers)
        logging.debug(result.content) 
        tree = html.fromstring(result.content)
        transactions = self._parse_transactions(tree)
        return transactions

    def get_form_key(self, url):
        """ Extract the private key used to validate form submissions """
        result = self.session.get(url)
        tree = html.fromstring(result.text)
        authenticity_token = list(set(tree.xpath("//input[@name='VALSRCKEY']/@value")))[0]
        return authenticity_token


    def _clean_up(self, raw_list):
        l = []
        for x in raw_list:
            x = x.strip()
            x = x.replace('$', '')
            x = x.replace(',', '')
            l.append(x)
        return l

    def _parse_transactions(self, tree):

        fund_name = tree.xpath("//tr[td/span/text()='Portfolio: ']/td/span/text()")[1]
        # Get all the dates, types(contribution), invested amount, unit price, number of units
        dates = self._clean_up(tree.xpath("//td[@class='ddcenter']/span/text()"))
        types = self._clean_up(tree.xpath("//td[@class='dddefault']/span/text()"))

        # Amounts need to be parsed in order
        _values = self._clean_up(tree.xpath("//td[@class='ddright']/span/text()"))
        invest_amounts = self._clean_up(_values[::4])  # First column, every fourth value
        prices = self._clean_up(_values[1::4])         # Second column
        units = self._clean_up(_values[2::4])         # Third column

        transactions = []
        for d,t,a,p,u in zip(dates, types, invest_amounts, prices, units):
            transactions.append(Transaction(fund_name, d, t, p, u, a))
        return transactions







