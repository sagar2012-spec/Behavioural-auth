// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HashStore {
    mapping(string => string) private hashes;

    function storeHash(string memory patternId, string memory hashValue) public {
        hashes[patternId] = hashValue;
    }

    function getHash(string memory patternId) public view returns (string memory) {
        return hashes[patternId];
    }
}