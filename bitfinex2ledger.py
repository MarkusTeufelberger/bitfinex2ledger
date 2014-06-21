# read csv files
import csv
# regular expressions for parsing descriptions
import re
# deal with timestamps + create them
import datetime


def parse_timestamp(timestamp):
    # since setting up locales is a pain in the ass sometimes
    # and works with different strings on different platforms...
    # ...let's just do this by hand and be done with it!
    if timestamp.startswith("January"):
        month = 1
    elif timestamp.startswith("February"):
        month = 2
    elif timestamp.startswith("March"):
        month = 3
    elif timestamp.startswith("April"):
        month = 4
    elif timestamp.startswith("May"):
        month = 5
    elif timestamp.startswith("June"):
        month = 6
    elif timestamp.startswith("July"):
        month = 7
    elif timestamp.startswith("August"):
        month = 8
    elif timestamp.startswith("September"):
        month = 9
    elif timestamp.startswith("October"):
        month = 10
    elif timestamp.startswith("November"):
        month = 11
    elif timestamp.startswith("December"):
        month = 12
    else:
        return "UNKNOWN TIMESTAMP FORMAT"
    # always at the same position from the end of the timestamp:
    day = int(timestamp[-26:-24])
    year = int(timestamp[-22:-18])
    return datetime.date(year, month, day).isoformat()


def process_ledger_line(line):
    ###########################################################################
    # header
    ###########################################################################

    if line == ['Currency', 'Description', 'Amount', 'Balance', 'Date']:
        return

    # do some small general data formating
    currency = line[0]
    timestamp = parse_timestamp(line[4])

    ###########################################################################
    # lending
    ###########################################################################
    # Note: Fees are already deducted here by the platform and not reported.
    #       If you want to see them in the actual ledger, you need to add a few
    #       extra calculations + transactions.
    #       Also historically these fees were changing quite a bit.

    # Interest Payment on wallet deposit
    if re.match(r"^Interest Payment on wallet (deposit|trading|exchange)$", line[1]):
        wallet = re.match(r"^Interest Payment on wallet (deposit|trading|exchange)$", line[1]).group(1).capitalize()

        print timestamp + " Interest received for lending " + currency
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tIncome:Bitfinex:Lending"

    # new name, old system - "Swap payments" for "liquidity swaps" is basically
    # interest, so the description still states "Interest".
    # Swap Payment on wallet deposit
    elif re.match(r"^Swap Payment on wallet (deposit|trading|exchange)$", line[1]):
        wallet = re.match(r"^Swap Payment on wallet (deposit|trading|exchange)$", line[1]).group(1).capitalize()

        print timestamp + " Interest received for lending " + currency
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tIncome:Bitfinex:Lending"

    ###########################################################################
    # affiliation
    ###########################################################################

    # Earned fees from user xxx on wallet trading
    elif re.match(r"^Earned fees from user \d+ on wallet (deposit|trading|exchange)$", line[1]):
        userid = re.match(r"^Earned fees from user (\d+) on wallet (deposit|trading|exchange)$", line[1]).group(1).capitalize()
        wallet = re.match(r"^Earned fees from user (\d+) on wallet (deposit|trading|exchange)$", line[1]).group(2).capitalize()

        print timestamp + " Affiliation income in " + currency
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tIncome:Bitfinex:Affiliation:User" + userid

    ###########################################################################
    # trading
    ###########################################################################

    # Trading fees for xxx.xxx BTC @ xxx.xxx on BFX (x.xx%) on wallet trading
    elif re.match(r"^Trading fees for \d+\.\d+ (BTC|USD|LTC) @ \d+\.\d+ on (BFX|BSTP|MTGOX) \(\d+\.\d+%\) on wallet (deposit|trading|exchange)$", line[1]):
        wallet = re.match(r"^Trading fees for (\d+\.\d+) (BTC|USD|LTC) @ (\d+\.\d+) on (BFX|BSTP|MTGOX) \((\d+\.\d+)%\) on wallet (deposit|trading|exchange)$", line[1]).group(6).capitalize()

        print timestamp + " Paid trading fees in " + currency + " for a trade"
        # this is a debit transaction!
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tExpenses:Bitfinex:Fees:Trade"

    # Position #xxx swap on wallet trading
    elif re.match(r"^Position #\d+ swap on wallet (deposit|trading|exchange)$", line[1]):
        positionid = re.match(r"^Position #(\d+) swap on wallet (deposit|trading|exchange)$", line[1]).group(1)
        wallet = re.match(r"^Position #(\d+) swap on wallet (deposit|trading|exchange)$", line[1]).group(2).capitalize()

        print timestamp + " (#" + positionid + ") Paid swap fees in " + currency + " for a trade"
        # this is a debit transaction!
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tExpenses:Bitfinex:Fees:Swap"

    # Position #xxx closed @ xxx.xxx on wallet trading
    elif re.match(r"^Position #\d+ closed @ \d+\.\d+ on wallet (deposit|trading|exchange)$", line[1]):
        positionid = re.match(r"^Position #(\d+) closed @ (\d+\.\d+) on wallet (deposit|trading|exchange)$", line[1]).group(1)
        wallet = re.match(r"^Position #(\d+) closed @ (\d+\.\d+) on wallet (deposit|trading|exchange)$", line[1]).group(3).capitalize()

        print timestamp + " (#" + positionid + ") Closed a trade and settled in " + currency
        # this can be a debit transaction!
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tIncome:Bitfinex:Trades:Close"

    # Position #xxx claimed @ xxx.xxx on wallet trading
    elif re.match(r"^Position #\d+ claimed @ \d+\.\d+ on wallet (deposit|trading|exchange)$", line[1]):
        positionid = re.match(r"^Position #(\d+) claimed @ (\d+\.\d+) on wallet (deposit|trading|exchange)$", line[1]).group(1)
        wallet = re.match(r"^Position #(\d+) claimed @ (\d+\.\d+) on wallet (deposit|trading|exchange)$", line[1]).group(3).capitalize()

        print timestamp + " (#" + positionid + ") Claimed a trade and settled in " + currency
        # this can be a debit transaction!
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tIncome:Bitfinex:Trades:Claim"

    # Position #xxx claimed @ xxx.xxx (fee: xxx.xxx BTC) on wallet trading
    elif re.match(r"^Position #\d+ claimed @ \d+\.\d+ \(fee: \d+\.\d+ (BTC|USD|LTC)\) on wallet (deposit|trading|exchange)$", line[1]):
        positionid = re.match(r"^Position #(\d+) claimed @ (\d+\.\d+) \(fee: (\d+\.\d+) (BTC|USD|LTC)\) on wallet (deposit|trading|exchange)$", line[1]).group(1)
        fee = re.match(r"^Position #(\d+) claimed @ (\d+\.\d+) \(fee: (\d+\.\d+) (BTC|USD|LTC)\) on wallet (deposit|trading|exchange)$", line[1]).group(3)
        feecurrency = re.match(r"^Position #(\d+) claimed @ (\d+\.\d+) \(fee: (\d+\.\d+) (BTC|USD|LTC)\) on wallet (deposit|trading|exchange)$", line[1]).group(4)
        wallet = re.match(r"^Position #(\d+) claimed @ (\d+\.\d+) \(fee: (\d+\.\d+) (BTC|USD|LTC)\) on wallet (deposit|trading|exchange)$", line[1]).group(5).capitalize()

        print timestamp + " (#" + positionid + ") Claimed a trade and settled in " + currency
        # this can be a debit transaction!
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tIncome:Bitfinex:Trades:Claim"

        # The fee is already deducted in the displayed amount, we first need to
        # credit it from income, then deduct it to expenses
        print timestamp + " (#" + positionid + ") Received fee for claimed trade in " + currency
        print "\tAssets:Bitfinex:" + wallet + "  \t" + fee + " " + feecurrency
        print "\tIncome:Bitfinex:Trades:Claim"
        print timestamp + " (#" + positionid + ") Paid fee for claimed trade in " + currency
        #                    note the minus here! -V-
        print "\tAssets:Bitfinex:" + wallet + "  \t-" + fee + " " + feecurrency
        print "\tExpenses:Bitfinex:Fees:Claim"

    # Settlement @ xxx.xxx on wallet trading
    elif re.match(r"^Settlement @ \d+\.\d+ on wallet (deposit|trading|exchange)$", line[1]):
        wallet = re.match(r"^Settlement @ (\d+\.\d+) on wallet (deposit|trading|exchange)$", line[1]).group(2).capitalize()

        print timestamp + " Force liquidated a trade and settled in " + currency
        # this can be a debit transaction!
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tIncome:Bitfinex:Trades:Settle"

    ###########################################################################
    # external deposits/withdrawals
    ###########################################################################

    # Wire Transfer Withdrawal #xxx on wallet deposit
    elif re.match(r"^Wire Transfer Withdrawal #\d+ on wallet (deposit|trading|exchange)$", line[1]):
        withdrawalid = re.match(r"^Wire Transfer Withdrawal #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(1)
        wallet = re.match(r"^Wire Transfer Withdrawal #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(2).capitalize()

        print timestamp + " (#" + withdrawalid + ") Wire withdrawal of " + currency
        # this is a debit transaction!
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        # you might want to change this ("Yourbank") to the bank account your
        # payment actually went to
        print "\tAssets:Yourbank:Bitfinex:Withdrawals"

    # Bitcoin Withdrawal #xxx on wallet deposit
    elif re.match(r"^Bitcoin Withdrawal #\d+ on wallet (deposit|trading|exchange)$", line[1]):
        withdrawalid = re.match(r"^Bitcoin Withdrawal #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(1)
        wallet = re.match(r"^Bitcoin Withdrawal #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(2).capitalize()

        print timestamp + " (#" + withdrawalid + ") Bitcoin withdrawal of " + currency
        # this is a debit transaction!
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        # you might want to change this to the account or maybe address your
        # Bitcoin payment actually went to
        print "\tAssets:Bitcoin:Bitfinex:Withdrawals"

    # Deposit (WIRE) #xxx on wallet deposit
    elif re.match(r"^Deposit \(WIRE\) #\d+ on wallet (deposit|trading|exchange)$", line[1]):
        depositid = re.match(r"^Deposit \(WIRE\) #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(1)
        wallet = re.match(r"^Deposit \(WIRE\) #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(2).capitalize()

        print timestamp + " (#" + depositid + ") Wire deposit of " + currency
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        # you might want to change this ("Yourbank") to the bank account your
        # payment actually originated from
        print "\tAssets:Yourbank:Bitfinex:Deposits"

    # Deposit (BITCOIN) #xxx on wallet deposit
    elif re.match(r"^Deposit \(BITCOIN\) #\d+ on wallet (deposit|trading|exchange)$", line[1]):
        depositid = re.match(r"^Deposit \(BITCOIN\) #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(1)
        wallet = re.match(r"^Deposit \(BITCOIN\) #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(2).capitalize()

        print timestamp + " (#" + depositid + ") Bitcoin deposit of " + currency
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        # you might want to change this to the account/addresss your payment
        # actually originated from
        print "\tAssets:Bitcoin:Bitfinex:Deposits"

    # TODO: Add Litecoin/Darkcoin lines - pull requests welcome

    ###########################################################################
    # internal movement between accounts
    ###########################################################################
    # Warning: entries are always in pairs here! One for crediting one account,
    # one debiting the other.
    # Just use one of them, discard the other

    # Transfer of x.xxx USD from wallet trading to deposit on wallet deposit
    elif re.match(r"^Transfer of \d+\.\d+ (BTC|USD|LTC) from wallet (deposit|trading|exchange) to (deposit|trading|exchange) on wallet (deposit|trading|exchange)$", line[1]):
        currency = re.match(r"^Transfer of (\d+\.\d+) (BTC|USD|LTC) from wallet (deposit|trading|exchange) to (deposit|trading|exchange) on wallet (deposit|trading|exchange)$", line[1]).group(2)
        fromwallet = re.match(r"^Transfer of (\d+\.\d+) (BTC|USD|LTC) from wallet (deposit|trading|exchange) to (deposit|trading|exchange) on wallet (deposit|trading|exchange)$", line[1]).group(3).capitalize()
        towallet = re.match(r"^Transfer of (\d+\.\d+) (BTC|USD|LTC) from wallet (deposit|trading|exchange) to (deposit|trading|exchange) on wallet (deposit|trading|exchange)$", line[1]).group(4).capitalize()
        onwallet = re.match(r"^Transfer of (\d+\.\d+) (BTC|USD|LTC) from wallet (deposit|trading|exchange) to (deposit|trading|exchange) on wallet (deposit|trading|exchange)$", line[1]).group(5).capitalize()
        if onwallet == towallet:
            # second line, disregard
            return
        print timestamp + " Moving " + currency + " between wallets"
        # this is always the debit transaction of the two (amount is negative at fromwallet)
        print "\tAssets:Bitfinex:" + fromwallet + "  \t" + line[2] + " " + currency
        print "\tAssets:Bitfinex:" + towallet

    ###########################################################################
    # internal balance adjustments by the platform
    ###########################################################################
    # Note: These transactions should be relatively rare
    #       One showed up once after a problem with interest calculation was
    #       discovered.
    #       It can be assumed that they are issued manually and will usually
    #       credit the user for money that was lost due to a platform error.

    # Adjustment #xxx on wallet trading
    elif re.match(r"^Adjustment #\d+ on wallet (deposit|trading|exchange)$", line[1]):
        adjustmentid = re.match(r"^Adjustment #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(1)
        wallet = re.match(r"^Adjustment #(\d+) on wallet (deposit|trading|exchange)$", line[1]).group(2).capitalize()

        print timestamp + " (#" + adjustmentid + ") Got balance adjusted by the platform in " + currency
        # this can be a debit transaction!
        # booked to income since it is assumed that adjustments are used to credit users for platform errors
        print "\tAssets:Bitfinex:" + wallet + "  \t" + line[2] + " " + currency
        print "\tIncome:Bitfinex:Adjustments"

    else:
        print "UNKNOWN line. Please report! DATA: ", line


try:
    with open('history_USD.csv', 'rb') as csvfile:
        myreader = csv.reader(csvfile)
        for row in myreader:
            process_ledger_line(row)
except:
    pass

try:
    with open('history_BTC.csv', 'rb') as csvfile:
        myreader = csv.reader(csvfile)
        for row in myreader:
            process_ledger_line(row)
except:
    pass

try:
    with open('history_LTC.csv', 'rb') as csvfile:
        myreader = csv.reader(csvfile)
        for row in myreader:
            process_ledger_line(row)
except:
    pass

try:
    with open('history_DRK.csv', 'rb') as csvfile:
        myreader = csv.reader(csvfile)
        for row in myreader:
            process_ledger_line(row)
except:
    pass
