# Paste below code in remix 
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FileRegistry {
    struct FileInfo {
        string filename;
        string fileHash;
        uint256 timestamp;
        address uploader;
    }

    FileInfo[] public files;

    event FileRegistered(
        uint256 index,
        string filename,
        string fileHash,
        uint256 timestamp,
        address uploader
    );

    function addFile(string memory _filename, string memory _fileHash) public {
        FileInfo memory newFile = FileInfo({
            filename: _filename,
            fileHash: _fileHash,
            timestamp: block.timestamp,
            uploader: msg.sender
        });

        files.push(newFile);

        emit FileRegistered(
            files.length - 1,
            _filename,
            _fileHash,
            block.timestamp,
            msg.sender
        );
    }

    function getFile(uint256 index)
        public
        view
        returns (
            string memory,
            string memory,
            uint256,
            address
        )
    {
        require(index < files.length, "Invalid index");
        FileInfo storage f = files[index];
        return (f.filename, f.fileHash, f.timestamp, f.uploader);
    }

    function getTotalFiles() public view returns (uint256) {
        return files.length;
    }
}
