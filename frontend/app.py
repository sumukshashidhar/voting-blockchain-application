from flask import Flask
import datetime
import json
from hashlib import sha256
import requests
from flask import render_template, redirect, request

app = Flask(__name__)

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/', methods=['GET'])
def index():
    fetch_posts()
    return render_template('index.html',
                           title='Voter Dashboard',
                           votes=[],
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/land', methods=['GET'])
def land():
    return render_template('landing.html')


@app.route('/error', methods=['GET'])
def index3():
    return render_template('error.html',
                           title='Voter Dashboard',
                           votes=[],
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/votes', methods=['GET'])
def index2():
    global posts
    print(posts)
    fetch_posts()
    return render_template('index2.html',
                           title='Blockchain Votes',
                           votes=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/changeNode', methods=['GET'])
def changeNode():
    CONNECTED_NODE_ADDRESS = "http://127.0.0.1:9000"
    return f'changed node to pper node {CONNECTED_NODE_ADDRESS}'


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    author = request.form["author"]
    password = request.form["password"]
    dob = request.form["dob"]
    print("Got: ", post_content, author, password, dob)

    if True:
        post_object = {
            'author': author,
            'content': sha256(post_content.encode()).hexdigest(),
        }

        # Submit a transaction
        new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

        requests.post(new_tx_address, json=post_object, headers={'Content-type': 'application/json'})

        return redirect('/')   
    else:
        return redirect('/error')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')