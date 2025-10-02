Blockchain-Based File Management System (Local Ganache Demo)

This project is a File Management System using Blockchain, built with:
 Ganache (Local Ethereum Blockchain)
 Remix IDE (Smart Contract Deployment)
 Flask + Web3.py (Python Backend)
 Bootstrap 5 (Frontend UI)

It stores file metadata (name, hash, timestamp) on a local blockchain, ensuring integrity and immutability.

 Features:
 Upload file & auto-generate SHA-256 hash
 Store metadata on Ganache blockchain
 View all uploaded files in a table
 Verify file integrity (detects tampering)
 Modern Bootstrap UI
 Local & offline (no real blockchain needed)

project-folder/
│
├── app.py                     # Flask backend
├── FileRegistry.sol           # Solidity smart contract
├── uploads/                  # Uploaded files stored here
└── templates/                # Frontend pages
    ├── base.html
    ├── index.html
    └── files.html

1. Install Requirements
Make sure Python 3 is installed, then run:
pip install flask web3

2. Run Ganache (Local Blockchain)
Option 1 – Ganache GUI:
Open Ganache
Create a New Workspace
Note the RPC port (default: 7545)
Option 2 – Ganache CLI:
ganache --port 7545

3. Deploy Smart Contract in Remix
Open  https://remix.ethereum.org
Create file: FileRegistry.sol
Paste the contract code
Compile it
Go to Deploy & Run
Select Injected Provider (MetaMask/Ganache)
Deploy → Copy:
 Contract Address
 ABI JSON
Paste them into app.py:
contract_address = "0xYourContractAddress"
contract_abi = [ ...ABI JSON... ]

4. Start Flask App
python app.py

Author
Hitesh Raktade
Blockchain Technology Project
(Flask + Solidity + Ganache)