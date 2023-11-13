from flask import Flask, jsonify, request
from web3 import Web3
from web3.middleware import geth_poa_middleware
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

app = Flask(__name__)

web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
web3.middleware_stack.inject(geth_poa_middleware, layer=0)

contract_source_code = """
pragma solidity ^0.8.0;

contract HealthRecords {
    address public owner;
    mapping(address => string) public medicalRecords;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can call this function");
        _;
    }

    function addRecord(string memory data) public onlyOwner {
        medicalRecords[msg.sender] = data;
    }
}
"""

def deploy_contract():
    account = web3.eth.accounts[0]  # Replace with your Ethereum account
    compiled_contract = compile_contract(contract_source_code)
    contract = web3.eth.contract(abi=compiled_contract['abi'], bytecode=compiled_contract['bin'])
    tx_hash = contract.constructor().transact({'from': account})
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    return contract(address=tx_receipt['contractAddress'])

def compile_contract(source_code):
    return web3.eth.compile.solidity(source_code)

X, y = [], []

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier()
model.fit(X_train, y_train)

@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.get_json()
    contract = deploy_contract()
    account = web3.eth.accounts[0]  # Replace with your Ethereum account
    contract.functions.addRecord(data['record']).transact({'from': account})
    prediction = model.predict([data['features']])
    return jsonify({'transaction_hash': 'transaction_hash', 'prediction': prediction.tolist()}), 200

if __name__ == '__main__':
    app.run(port=5000)
