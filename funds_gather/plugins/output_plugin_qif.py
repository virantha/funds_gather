
class OutputPluginQif(object):

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



