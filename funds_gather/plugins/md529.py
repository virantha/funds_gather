import requests
from lxml import html
import logging
import dateparser
from transaction import *

from collections import namedtuple

class MD529(object):

    urls = { 'home': 'https://secure.collegesavingsmd.org/pls/prod/twpkwbis.P_WWWLogin',
             'login': 'https://secure.collegesavingsmd.org/pls/prod/twpkwbis.P_ValLogin',
             'acct_summary': 'https://secure.collegesavingsmd.org/pls/prod/hwtkpage.P_HomePage',
             'acct_select': 'https://secure.collegesavingsmd.org/pls/prod/hwtkstmt.P_DispYearChoice',
             'transactions': 'https://secure.collegesavingsmd.org/pls/prod/hwtkstmt_MD.P_DispAcctStmt',
            }

    FundRecord = namedtuple('FundRecord', 'name, ticker, cusip')
    # Use the tickers from Bloomberg; these are not real funds available on finance sites to lookup, but
    # I need something for the CUSIP field and ticker.
    fund_mapping = [ ['Portfolio 2036', '5392164:US', '5292164US'],
                     ['Portfolio 2033', '5392163:US', '5292163US'],
                     ['Portfolio 2030', '5291623:US  ', '5291623US'],
                     ['Portfolio 2027', '5290957:US', '5290957US'],
                     ['Portfolio 2024', '5290956:US', '5290956US'],
                     ['Portfolio 2021', '5290955:US', '5290955US'],
                     ['Portfolio 2018', '5290954:US', '5290954US'],
                     ['Portfolio for College', '5290951:US', '5290951US'],
                     ['Balanced Portfolio', '5290960:US', '5290960US'],
                     ['Equity Portfolio', '5290958:US', '5290958US'],
                     ['Inflation Focused Bond Port', '5290952:US', '5290962US'],
                     ['Global Equity Mkt Index Port', '5290959:US', '5290959US'],
                     ['Bond and Income Portfolio', '5290961:US', '5290961US'],

                   ]

    def __init__(self):
        self.session = requests.session()
        self.funds = { x[0]: Fund(*x) for x in self.fund_mapping}

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
        logging.debug(result.text)
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
        transactions = self._parse_transactions(tree, account)
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

    def _parse_transactions(self, tree, account_number):

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
        if fund_name in self.funds:
            fund = self.funds[fund_name]
        else:
            print("WARNING: Fund name %s not known" % fund_name)
            fund = Fund(fund_name, 'UNKNOWN', 'UNKNOWN')

        account = Account('Maryland 520 College Investment Plan', account_number)
        dates = [dateparser.parse(d) for d in dates]
        for d,t,a,p,u in zip(dates, types, invest_amounts, prices, units):
            transactions.append(Transaction(fund, d, t, p, u, a, account))
        return transactions







