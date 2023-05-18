import json
import time

from server.block import Block


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.chain = []
        self.pending_transactions = []

    def First_block(self):
        first_block = Block([], 0, "0", 0)
        first_block.hash = first_block.__hash__()
        with open("../blocks/" + first_block.hash + ".json", 'w') as outfile:
            json.dump(self.__dict__, outfile)
        self.chain.append(first_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.hash)

    def add_mined_block(self, block):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False
        self.chain.append(block)
        return True

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block ,proof):
            return False
        block.hash = proof

        self.chain.append(block)
        return True

    def add_new_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def proof_of_work(self, block):
        block.nonce = 0
        hash_computed = block.__hash__()
        while not hash_computed.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            hash_computed = block.__hash__()
        return hash_computed

    def mine(self):
        if not self.pending_transactions:
            return False

        last_block = self.last_block

        new_block = Block(transactions=self.pending_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash, height=last_block.height + 1)

        proof = self.proof_of_work(new_block)
        with open("../blocks/" + proof + ".json", 'w') as outfile:
            json.dump(new_block.__dict__, outfile)
        result = self.add_block(new_block, proof)
        self.pending_transactions = []

        return result
