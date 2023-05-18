
Instructions to run the code -
1) Start the 3 server nodes
server/server_flask1.py  --- runs at port 5001
server/server_flask2.py ---- runs at port 5002
server/server_flask3.py  --- runs at port 5003

2) run client/main.py -- this is used to register the nodes with each other.

3) run client/wallet1.py and client/wallet2.py --

      user_input 1 - check users balance
      user_input 2 - check other wallet balance
      user_input 3 - do a transaction. ( creditor adress should be given)
      user_input 4 -  mine the block.
      user_input 5 - see the synchronised blockchain data in all the peers.

4) proof of work is added in blockchain.py at /mine end point.
 Note -
 Blocks folder - stores the blocks in blockchain
 Transactions folder - stores the transactions
 Server/keys -  public , private keys of the user.
 Cleint/Storage - stores the private key for authentication purpose.




