# Copyright 2016 Virantha Ekanayake All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

Usage:
    funds_gather.py [options] <username> <password> all
    funds_gather.py [options] <username> <password> (%s)...
    funds_gather.py --conf=FILE
    funds_gather.py -h

Arguments:
    username    Login name
    password    Login password
    all         Run all steps in the flow (%s)
%s

Options:
    -h --help        show this message
    -v --verbose     show more information
    -d --debug       show even more information
    --version        show version
    --out=FILE       output filename [default: out.qif] 
    --conf=FILE      load options from file

"""

from docopt import docopt
import yaml
import sys, os, logging, shutil
from collections import OrderedDict
from schema import Schema, And, Optional, Or, Use, SchemaError



from version import __version__
from utils import ordered_load, merge_args
from plugins.md529 import MD529
from plugins.output_plugin_qif import OutputPluginQif


"""
   
.. automodule:: funds_gather
    :private-members:
"""

class FundsGather(object):
    """
        The main clas.  Performs the following functions:

    """

    def __init__ (self):
        """ 
        """
        self.args = None
        self.flow = OrderedDict([ ('download', 'Download all transactions from accounts'),
                                  ('qif',      'Save downloaded transactions to qif'),
                      ])



    def get_options(self, argv):
        """
            Parse the command-line options and set the following object properties:

            :param argv: usually just sys.argv[1:]
            :returns: Nothing

            :ivar debug: Enable logging debug statements
            :ivar verbose: Enable verbose logging
            :ivar config: Dict of the config file

        """
        padding = max([len(x) for x in self.flow.keys()]) # Find max length of flow step names for padding with white space
        docstring = __doc__ % ('|'.join(self.flow), 
                              ','.join(self.flow.keys()),
                              '\n'.join(['    '+k+' '*(padding+4-len(k))+v for k,v  in self.flow.items()]))
        args = docopt(docstring, version=__version__)

        # Load in default conf values from file if specified
        if args['--conf']:
            with open(args['--conf']) as f:
                conf_args = yaml.load(f)
        else:
            conf_args = {}
        args = merge_args(conf_args, args)

        schema = Schema({
            '<username>': And(str, len),
            '<password>': And(str, len),
            '--out': And(str, len),
            object: object
            })
        try:
            args = schema.validate(args)
        except SchemaError as e:
            exit(e)

        if args['all'] == 0:
            for f in list(self.flow):
                if args[f] == 0: del self.flow[f]
            logging.info("Doing flow steps: %s" % (','.join(self.flow.keys())))

        self.output_file = args['--out']

        if args['--debug']:
            logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        elif args['--verbose']:
            logging.basicConfig(level=logging.INFO, format='%(message)s')   

        self.args = args # Just save this for posterity



    def go(self, argv):
        """ 
            The main entry point into FundsGather

            #. Do something
            #. Do something else
        """
        # Read the command line options
        self.get_options(argv)
        if 'download' in self.flow:
            acct = MD529()
            acct.login(self.args['<username>'], self.args['<password>'])
            acct_numbers = acct.get_accounts()
            transactions = []
            for acct_number in acct_numbers:
                trans = acct.get_transactions(acct_number)
                transactions += trans
                for tran in trans:
                    print(str(tran))
            
            if 'qif' in self.flow:
                out = OutputPluginQif()
                out.emit(self.output_file, transactions)


def main():
    script = FundsGather()
    script.go(sys.argv[1:])

if __name__ == '__main__':
    main()

