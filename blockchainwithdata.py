# For timestamp
import datetime

import requests
# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib

# To store data
# in our blockchain
import json

# Flask is for creating the web
# app and jsonify is for
# displaying the blockchain
from flask import Flask, jsonify,render_template,request

class Blockchain:
	
	# This function is created
	# to create the very first
	# block and set it's hash to "0"
	def __init__(self):
		self.chain = []
		self.create_block(proof=1, previous_hash='0', veh="XXXX", RSA_ID="SERVER", loc="NA")

	# This function is created
	# to add further blocks
	# into the chain
	def create_block(self, proof, previous_hash,veh,loc,RSA_ID):
		block = {'Index': len(self.chain) + 1,
				'Timestamp': str(datetime.datetime.now()),
				'Proof': proof,
				'Previous_hash': previous_hash,
				'RSA Location' : loc,
				'RSA ID' : RSA_ID,
				'Vehicles Details':veh}
		self.chain.append(block)
		return block
		
	# This function is created
	# to display the previous block
	def print_previous_block(self):
		return self.chain[-1]
		
	# This is the function for proof of work
	# and used to successfully mine the block
	def proof_of_work(self, previous_proof):
		new_proof = 1
		check_proof = False
		
		while check_proof is False:
			hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
			if hash_operation[:4] == '0000':
				check_proof = True
			else:
				new_proof += 1
		return new_proof

	def hash(self, block):
		encoded_block = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(encoded_block).hexdigest()

	def chain_valid(self, chain):
		previous_block = chain[0]
		block_index = 1
		
		while block_index < len(chain):
			block = chain[block_index]
			if block['Previous_hash'] != self.hash(previous_block):
				return False
				
			previous_proof = previous_block['Proof']
			proof = block['Proof']
			hash_operation = hashlib.sha256(
				str(proof**2 - previous_proof**2).encode()).hexdigest()
			
			if hash_operation[:4] != '0000':
				return False
			previous_block = block
			block_index += 1
		
		return True


# Creating the Web
# App using flask
app = Flask(__name__)
app.debug

# Create the object
# of the class blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods=['GET'])
def index():
   return render_template('Block.html')

@app.route('/block', methods=['POST'])
def mine_block():
	veh={}
	previous_block = blockchain.print_previous_block()
	previous_proof = previous_block['Proof']
	proof = blockchain.proof_of_work(previous_proof)
	previous_hash = blockchain.hash(previous_block)
	cou = request.form.get('i') 
	cou = int(cou)
	loc = request.form.get('location')
	RSA_ID = request.form.get('RSAID')
	for i in range(1,cou+1):
		id = request.form.get('car[%d][number]' % (i))
		dest = request.form.get('car[%d][dest]' % (i))
		vel = request.form.get('car[%d][speed]' % (i))
		vel	= int(vel)
		veh[i]={}
		veh[i]['ID']=id
		veh[i]['Destination']=dest
		veh[i]['Speed']='%d Km/H' % (vel)
	block = blockchain.create_block(proof, previous_hash, veh, loc, RSA_ID)
 	
	response = {'Message': 'A block is MINED',
				'Index': block['Index'],
				'Timestamp': block['Timestamp'],
				'Proof': block['Proof'],
				'Previous_hash': block['Previous_hash'],
				'RSA Location' : block['RSA Location'],
                'Vehicle Details': block['Vehicles Details']}
	return jsonify(response), 200

# Display blockchain in json format
@app.route('/get_chain', methods=['GET'])
def display_chain():
	response = {'chain': blockchain.chain,
				'length': len(blockchain.chain)}
	return jsonify(response), 200

# Check validity of blockchain
@app.route('/valid', methods=['GET'])
def valid():
	valid = blockchain.chain_valid(blockchain.chain)
	
	if valid:
		response = {'message': 'The Blockchain is valid.'}
	else:
		response = {'message': 'The Blockchain is not valid.'}
	return jsonify(response), 200


# Run the flask server locally
app.run(host= "0.0.0.0")