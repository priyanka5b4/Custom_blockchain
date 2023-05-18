import json
import os
import datetime

import requests
import rsa

from client import  transaction


# echo-client.py


# getting users data
from server.digital_sign_utility import load_Private_key, sign_sha1, load_Public_key


def verify_sha1(msg, signature, publick_key):
    try:
        return rsa.verify(msg, signature, publick_key) == 'SHA-1'
    except:
        return False


def get_wallet_data():
    response = requests.get('http://127.0.0.1:5001/get_users')
    print(response.json())


# send the transaction object to blockchain server
def send_post(tranobj):
    res = requests.post('http://127.0.0.1:5001/post_new_transaction', json=tranobj)
    print(res.status_code)
    if res.status_code == 200:
        return 'success'
    else:
        return 'failure'


# mine the transactions that are there.
def mine():
    response = requests.get('http://127.0.0.1:5001/mine')
    print(response.text)
    return response.text


def get_balance(user_id):
    response = requests.get('http://127.0.0.1:5001/get_balance?user_name=' + user_id)
    print(response.text)


def get_user_adress(user_id):
    response = requests.get('http://127.0.0.1:5001/get_address?user_name=' + user_id)
    print(response.text)
    return response.text

# get chain details
def get_chain_details1():
    res = requests.get('http://127.0.0.1:5001/block_chain')
    return res


def get_chain_details2():
    res = requests.get('http://127.0.0.1:5002/block_chain')
    return res


def get_chain_details3():
    res = requests.get('http://127.0.0.1:5003/block_chain')
    return res


def check_signing(data):
    # verify the transaction details before adding to pending transactions
    user_name = data.get("user_name")
    signature = bytes.fromhex(data.get("signature"))
    public_key = load_Public_key('../Server/keys/public_key_' + user_name)
    data.pop("user_name")
    data.pop("signature")
    if verify_sha1(json.dumps(data).encode('UTF-8'), signature, public_key) == True:
        print("success")
    else:
        print("failure")


get_wallet_data()
username = input("enter your username to access your wallet ")
user_check = 0
i = 0
flag2 = 0

if os.path.exists('Storage/private_key_' + username + '.pem'):
    user_check = 1
    current_user_adress = get_user_adress(username)
    if user_check == 1:
        while flag2 == 0:

            user_input = input(
                "welcome to the your wallet Please enter your choice \n1)check my wallet balance \n2) check other "
                "wallet balance "
                "\n3)Do a transaction \n4)Mine the block \n5) Check synchronized data in nodes\npress any other key "
                "to stop ")

            if user_input == "1":
                get_balance(username)

            elif user_input == "2":
                user_name = input("get the name of other wallet")
                get_balance(user_name)

            elif user_input == "4":
                mine()
            elif user_input == "5":
                res = get_chain_details1()
                print(res.text)
                res = get_chain_details2()
                print(res.text)
                res = get_chain_details3()
                print(res.text)
            elif user_input == "3":
                tempDict = {}
                ToAdress = input("Please enter the creditor adress ")
                Amount = input("Please enter the amount to be debited")
                tempDict['FromAdress'] = current_user_adress
                tempDict['ToAdress'] = ToAdress
                tempDict['Amount'] = Amount
                ct = datetime.datetime.now()
                tempDict['timestamp'] = str(ct)
                get_wallet_data()
                private_key = load_Private_key('Storage/private_key_' + username + '.pem')
                tranobj = transaction.Transaction(tempDict.get('FromAdress'), tempDict.get('ToAdress'),
                                                  tempDict.get('Amount'), tempDict.get('timestamp'))
                tranobj.__hash__()
                # sign the transaction

                signature = sign_sha1(json.dumps(tranobj.transactionDetails).encode('UTF-8'), private_key)
                transactonDetails = tranobj.transactionDetails
                transactonDetails["signature"] = signature.hex()
                transactonDetails["user_name"] = username
                res = send_post(transactonDetails)
                check_signing(transactonDetails)
                if res == 'success':
                    print('Transaction completed')
                else:
                    print("Transaction not completed")

            else:
                flag2 = 1

# creating public and private key pair for the new user
if user_check == 0:
    print("wallet not present. Create a new wallet")
    user_name = input('please enter your username')
    url = 'http://127.0.0.1:5001/login'
    response = requests.get(url + '?user_id=' + user_name)
    print(response.text)
    with open('Storage/private_key_' + user_name + '.pem', 'wb') as f:
        f.write(response.content)




