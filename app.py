import os
import json
import hashlib
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from web3 import Web3
from config import RPC_URL, CONTRACT_ADDRESS, ABI_PATH, UPLOAD_FOLDER, MAX_CONTENT_LENGTH

app = Flask(__name__)
app.secret_key = "replace_with_a_secret_key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# connect to Ganache
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise RuntimeError(f"Cannot connect to RPC at {RPC_URL}. Start Ganache and try again.")

# use first Ganache account as default account
if len(w3.eth.accounts) == 0:
    raise RuntimeError("No accounts available from Ganache. Check Ganache app.")
default_account = w3.eth.accounts[0]
w3.eth.default_account = default_account

# load contract ABI and create contract object
try:
    with open(ABI_PATH, "r") as f:
        abi = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"Contract ABI not found at {ABI_PATH}")

contract_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
contract = w3.eth.contract(address=contract_address, abi=abi)

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

@app.route("/")
def index():
    try:
        # Fetch the file count from the blockchain
        file_count = contract.functions.getFileCount().call()
    except Exception as e:
        # Handle case where contract call fails (e.g., Ganache is down)
        print(f"Error fetching file count from contract: {e}")
        flash(f"Error connecting to blockchain for status: {e}", "error")
        file_count = "N/A"
    
    # Pass the count to the index.html template
    return render_template("index.html", file_count=file_count)

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        flash("No file part")
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash("No selected file")
        return redirect(url_for('index'))
    
    original_filename = secure_filename(file.filename)
    filename = original_filename
    
    # Ensure unique filename to prevent overwriting
    counter = 1
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    while os.path.exists(save_path):
        name, ext = os.path.splitext(original_filename)
        filename = f"{name}_{counter}{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        counter += 1

    file.save(save_path)

    # compute sha256
    file_hash = sha256_of_file(save_path)

    # store on chain
    try:
        tx_hash = contract.functions.addFile(filename, file_hash).transact({'from': w3.eth.default_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        flash(f"File uploaded and metadata stored on chain. Tx: {tx_hash.hex()}")
    except Exception as e:
        flash(f"Blockchain transaction failed: {str(e)}")
        # optionally remove saved file on failure
        # os.remove(save_path)
        return redirect(url_for('index'))

    return redirect(url_for('files'))

@app.route("/files")
def files():
    try:
        count = contract.functions.getFileCount().call()
    except Exception as e:
        flash(f"Failed to read from contract: {e}")
        count = 0
    records = []
    for i in range(count):
        try:
            # We access the file details using the index (i)
            idx, fname, fhash, ts, uploader = contract.functions.getFile(i).call()
            records.append({
                "index": idx,
                "filename": fname,
                "fileHash": fhash,
                "timestamp": ts,
                "uploader": ts, # Assuming uploader is retrieved as uploader
                "uploader": uploader
            })
        except Exception as e:
            # Handle case where an index might be invalid or a specific record fetch fails
            print(f"Error fetching file index {i}: {e}")
            continue

    return render_template("files.html", records=records)

@app.route("/verify/<int:index>")
def verify(index):
    # fetch on-chain hash
    try:
        idx, fname, fhash, ts, uploader = contract.functions.getFile(index).call()
    except Exception as e:
        flash(f"Error reading file: {e}")
        return redirect(url_for('files'))

    local_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
    if not os.path.exists(local_path):
        flash("Local file not found; stored only on chain or uploaded elsewhere.")
        return redirect(url_for('files'))

    local_hash = sha256_of_file(local_path)
    if local_hash == fhash:
        flash(f"Integrity OK for {fname} (index {index}).")
    else:
        flash(f"Integrity FAILED for {fname} (index {index}). On-chain: {fhash}, Local: {local_hash}")
    return redirect(url_for('files'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
