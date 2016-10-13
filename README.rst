FundsGather
============

|image_pypi| |image_downloads| |image_license| |passing| |quality| |Coverage Status|

FundsGather is a script to gather your financial fund information from accounts that do not support standard banking file exports such as QFX, OFX, QIF or even direct connect.
Currently, this program supports downloading transactions from Maryland's 529 College Savings plans and exporting to QIF, for import into your financial software like Quicken,
Banktivity, or MoneyDance.  An OFX/QFX plugin is also in the works.

* Free and open-source software: ASL2 license
* Blog: http://virantha.com/category/projects/funds_gather
* Documentation: http://virantha.github.io/funds_gather/html
* Source: https://github.com/virantha/funds_gather

Features
########


* Import from web account of Maryland 529 College Savings of all accounts tied to user.
* Export to QIF file.

Right now, the functionality is fairly rudimentary, but I intend to develop this more in the months to come.  Here's my todo list:

* Export to QFX/OFX (depending on what my financial software supports, it would be easier to write a plugin for XML compliant format)
* Import other types of transactions (right now, only buys are supported)
* Import other web sites

Usage:
######
See help for now:

::
    
    $ funds_gather -h

    Usage:
        funds_gather.py [options] <username> <password> all
        funds_gather.py [options] <username> <password> (download|qif)...
        funds_gather.py --conf=FILE
        funds_gather.py -h
     
    Arguments:
        username    Login name
        password    Login password
        all         Run all steps in the flow (download,qif)
        download    Download all transactions from accounts
        qif         Save downloaded transactions to qif
     
    Options:
        -h --help        show this message
        -v --verbose     show more information
        -d --debug       show even more information
        --version        show version
        --out=FILE       output filename [default: out.qif] 
        --conf=FILE      load options from file


Installation
############

::

    $ pip install funds_gather

Disclaimer
##########

The software is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

.. |image_pypi| image:: https://badge.fury.io/py/funds_gather.png
   :target: https://pypi.python.org/pypi/funds_gather
.. |image_downloads| image:: https://pypip.in/d/funds_gather/badge.png
   :target: https://crate.io/packages/funds_gather?version=latest
.. |image_license| image:: https://pypip.in/license/funds_gather/badge.png
.. |passing| image:: https://scrutinizer-ci.com/g/virantha/funds_gather/badges/build.png?b=master
.. |quality| image:: https://scrutinizer-ci.com/g/virantha/funds_gather/badges/quality-score.png?b=master
.. |Coverage Status| image:: https://coveralls.io/repos/virantha/funds_gather/badge.png?branch=develop
   :target: https://coveralls.io/r/virantha/funds_gather
