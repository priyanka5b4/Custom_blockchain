import hashlib
import json


class Block:

    def __init__(self, transactions, timestamp, previous_hash, height):
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.height = height

    def __hash__(self):
        hashvalue = hashlib.sha256(json.dumps(self.__dict__, sort_keys=True).encode('utf-8')).hexdigest()
        return hashvalue
