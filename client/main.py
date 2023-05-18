import requests


def send_post_req1():
    res = requests.post('http://127.0.0.1:5002/register_with', json={"node_address": "http://127.0.0.1:5001"},
                        headers={'Content-Type': 'application/json'})

    print(res.text + "of node at port 5002")


def send_post_req2():
    res = requests.post('http://127.0.0.1:5003/register_with', json={"node_address": "http://127.0.0.1:5001"},
                        headers={'Content-Type': 'application/json'})
    print(res.text + " of node at port 5003")


#  registering all the 3 nodes together to synchronize the data
send_post_req1()
send_post_req2()
