bitfinex2ledger
===============

Converter for Bitfinex CSV files to ledger-cli format.

Bitfinex CSV files are available at https://www.bitfinex.com/account/ledger once you are logged in. It is assumed that you keep their default name (history_[USD/BTC/LTC/DRK].csv) and copy them to the same directory as this script.

Writes output to stdout, so you need to pipe this to a file of your choice.

It basically is just a huge switch statement with some regex.
If a line is not recognized, it will print "UNKNOWN line. Please report! DATA: ...".
This usually will throw an error once ledger tries to parse the resulting file.

Either fix it yourself and (ideally) submit a pull request or post the DATA part (_exact_ same formatting, numbers can be obscured/replaced by xxx) as issue so I can fix it.

More info about ledger: http://ledger-cli.org

Usage:
======
Generate file in ledger format:
```
python2 bitfinex2ledger.py > bitfinex.ledger
```

Run ledger to display account balances:
```
ledger b -f bitfinex.ledger
```

License:
========
> All rights reserved, this program comes with no warranty, might eat your hamster, you're out on your own, yada, yada, yada...

> Seriously, this just parses a text file - if you want to use or extend this, feel free to do so.
