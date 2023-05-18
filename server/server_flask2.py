import hashlib
import json
import os

import flask
from flask import Flask, request
import requests
from server.block import Block
from server.blockchain import Blockchain
from server.digital_sign_utility import generate_keys, load_Public_key, verify_sha1

app = Flask(__name__)
peers = set()

# blockchain
blockchain = Blockchain()
blockchain.First_block()


def append_to_list(filename, obj):
    listObj = []

    # Check if file exists
    if os.path.isfile(filename) is False:
        raise Exception("File not found")

    # Read JSON file
    with open(filename) as fp:
        listObj = json.load(fp)

    # Verify existing list
    print(listObj)

    listObj.append(obj)

    # Verify updated list
    print(listObj)

    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file,
                  indent=4,
                  separators=(',', ': '))

    print('Successfully added to the list')


@app.route('/login', methods=['GET'])
def user():
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        generate_keys('keys/public_key_' + user_id, 'keys/private_key_' + user_id)
        public_key = load_Public_key('keys/public_key_' + user_id)
        adress = hashlib.sha256(json.dumps(public_key.n).encode('utf-8')).hexdigest()
        tempdict = {'username': user_id, 'address': adress, 'balance': '1000'}
        append_to_list("users.json", tempdict)
        return flask.send_from_directory('Keys',
                                         'private_key_' + user_id, as_attachment=True)


@app.route('/get_users', methods=['GET'])
def get_users():
    if request.method == 'GET':
        with open("users.json") as fp:
            users = json.load(fp)
            return json.dumps(users)


@app.route('/get_balance', methods=['GET'])
def get_balance():
    if request.method == 'GET':
        user_id = request.args.get('user_name')
        with open('users.json') as f:
            users = json.load(f)
            for user in users:
                if user.get('username') == user_id:
                    return user.get('balance')
            return 'user not found'


@app.route('/get_address', methods=['GET'])
def get_address():
    if request.method == 'GET':
        user_id = request.args.get('user_name')
        with open('users.json') as f:
            users = json.load(f)
            for user in users:
                if user.get('username') == user_id:
                    return user.get('address')
            return 'user not found'


# end point for post request
@app.route('/post_new_transaction', methods=['POST'])
def new_transaction():
    data = request.get_json()
    required_fields = ["FromAdress", "ToAdress", "Amount", "signature", "user_name"]

    for field in required_fields:
        if not data.get(field):
            return "Invalid transaction data", 404

    # verify the transaction details before adding to pending transactions
    user_name = data.get("user_name")
    signature = bytes.fromhex(data.get("signature"))
    public_key = load_Public_key('keys/public_key_' + user_name)
    data.pop("user_name")
    data.pop("signature")
    if verify_sha1(json.dumps(data).encode('UTF-8'), signature, public_key) == True:
        users = []
        blockchain.add_new_transaction(data)
        with open('users.json') as f:
            users = json.load(f)
            f.close()
        for user in users:
            if user.get('address') == data.get('ToAdress'):
                user['balance'] = str(int(user['balance']) + int(data.get('Amount')))
            if user.get('address') == data.get('FromAdress'):
                user['balance'] = str(int(user['balance']) - int(data.get('Amount')))
        with open("users.json", 'w') as json_file:
            json.dump(users, json_file,
                      indent=4,
                      separators=(',', ': '))
        json_file.close()

        return user.get('address')

        return "Success", 200
    else:
        return "Data Tampered", 404


# endpoint to return the node's copy of the chain.
@app.route('/block_chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# endpoint to mine
@app.route('/mine', methods=['GET'])
def mine_pending_transactions():

    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.height)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.First_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(
            block_data["transactions"],
            block_data["timestamp"],
            block_data["previous_hash"],
            block_data["height"])

        added = generated_blockchain.add_mined_block(block)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


# endpoint to add a block mined by someone else to chain
@app.route('/add_block', methods=['POST'])
def Add_block():
    block_data = request.get_json()
    block = Block(
        block_data["transactions"],
        block_data["timestamp"],
        block_data["previous_hash"],
        block_data["height"],
        block_data["nonce"],
        block_data["hash"])

    added = blockchain.add_mined_block(block)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.pending_transactions)


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}block_chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len:
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)


if __name__ == '__main__':
    app.run(port=5002)
