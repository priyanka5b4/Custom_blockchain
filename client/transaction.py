import hashlib
import json


class Transaction:
    transactionDetails = {}

    def __init__(self, FromAdress, ToAdress, Amount, timestamp):
        # Instance Variable
        self.transactionDetails['FromAdress'] = FromAdress
        self.transactionDetails['ToAdress'] = ToAdress
        self.transactionDetails['Amount'] = Amount
        self.transactionDetails['timestamp'] = timestamp

    def __hash__(self):
        self.transactionDetails["hashvalue"] = hashlib.sha256(
            json.dumps(self.transactionDetails).encode('utf-8')).hexdigest()
        with open('../transactions/' + self.transactionDetails["hashvalue"] + '.json', 'w') as outfile:
            json.dump(self.transactionDetails, outfile)
        print(" Transacation file saved")
