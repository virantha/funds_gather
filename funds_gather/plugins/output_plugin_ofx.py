from templet import templet
import datetime
from transaction import Transaction
import md5

class OutputPluginOfx(object):

    def __init__(self):
        pass

    def emit(self, filename, transactions):
        with open(filename, 'w') as f:
            f.write('!Type:Invst\n')
            for t in transactions:
                f.write('D%s\n' % t.date)
                f.write('NBuy\n')
                f.write('M%s\n' % t.trans_type)
                f.write('Y%s\n' % t.fund_id)
                f.write('I%s\n' % t.unit_price)
                f.write('Q%s\n' % t.units)
                f.write('T%s\n' % t.invest_amount)
                f.write('CX\n^\n')

    @templet
    def get_security_info(self, security):
        """
        <MFINFO>
        <SECINFO>
        <SECID>
        <UNIQUEID>${security.cusip}
        <UNIQUEIDTYPE>CUSIP
        </SECID>

        <SECNAME>${security.name}
        <TICKER>${security.ticker}
        </SECINFO>

        </MFINFO>
        """
    @templet
    def get_buy_transaction(self, transaction):
        """
        <BUYMF>
        <INVBUY>
        <INVTRAN>
        <FITID>${{
            m = md5.new()
            m.update(str(transaction))
            out.append(m.hexdigest())
        }}

        <DTTRADE>${transaction.date.strftime('%Y%m%d%H%M%S.0000')}[-5:EST]
        <DTSETTLE>${transaction.date.strftime('%Y%m%d%H%M%S.0000')}[-5:EST]
        <MEMO>${transaction.trans_type}
        </INVTRAN>
        <SECID>
        <UNIQUEID>${transaction.fund.cusip}
        <UNIQUEIDTYPE>CUSIP
        </SECID>

        <UNITS>${transaction.units}
        <UNITPRICE>${transaction.unit_price}
        <TOTAL>${transaction.invest_amount}
        <SUBACCTSEC>OTHER
        <SUBACCTFUND>OTHER

        </INVBUY>
        <BUYTYPE>BUY
        </BUYMF>

        """
    @templet
    def test(self, broker, transactions, securities):
        """
        OFXHEADER:100
        DATA:OFXSGML
        VERSION:103
        SECURITY:NONE
        ENCODING:USASCII
        CHARSET:1252
        COMPRESSION:NONE
        OLDFILEUID:NONE
        NEWFILEUID:NONE

        <OFX>
        <SIGNONMSGSRSV1>
        <SONRS>
        <STATUS>
        <CODE>0
        <SEVERITY>INFO
        <MESSAGE>SUCCESS
        </STATUS>

        <DTSERVER>${ broker.date }[-5:EST]

        <LANGUAGE>ENG
        </SONRS>
        </SIGNONMSGSRSV1>

        <INVSTMTMSGSRSV1>
        <INVSTMTTRNRS>
        <TRNUID>0
        <STATUS>
        <CODE>0
        <SEVERITY>INFO
        <MESSAGE>SUCCESS
        </STATUS>

        <INVSTMTRS>
        <DTASOF>${ broker.date }[-5:EST]
        <CURDEF>USD
        <INVACCTFROM>
        <BROKERID>${ broker.name }
        <ACCTID>${ broker.account_number }
        </INVACCTFROM>

        <INVTRANLIST>
        ${[x for x in transactions]}
        </INVTRANLIST>

        </INVSTMTRS>
        </INVSTMTTRNRS>
        </INVSTMTMSGSRSV1>

        <SECLISTMSGSRSV1>
        <SECLIST>
        ${[x for x in securities]}
        </SECLIST>
        </SECLISTMSGSRSV1>

        </OFX>
        """

    def emit(self, filename, transactions):
        trans_text = [self.get_buy_transaction(t) for t in transactions]
        securities = set()
        accounts = set()
        for t in transactions:
            securities.add(t.fund)
            accounts.add(t.account)
        assert len(accounts)==1, 'Uh oh, multiple accounts not supported in ofx output'
        account = accounts.pop()
        account.date = datetime.datetime.today().strftime('%Y%m%d%H%M%S.0000')
        securities_text = [self.get_security_info(s) for s in securities]
        with open(filename, 'w') as f:
            f.write(self.test(account, trans_text, securities_text))





if __name__ == '__main__':
    a = OutputPluginOfx()
    td = datetime.datetime.today()

    broker = {'id': 'collegesavingsmd.org',
               'account_id': '1234',
               'datetime': td.strftime('%Y%m%d%H%M%S.0000')
               }
    t = Transaction('MD portfolio 2033', td, 'Buy', '12.08', '10', '120.80')
    t.cusid = '999999999'
    t.fitid = '1111111111'
    tran = a.get_buy_transaction(t)

    print (a.test(broker, [tran]))

