pragma solidity ^0.5.5;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

contract AIAlienAnimals is ERC721Full {
    constructor() public ERC721Full("AI Alien Animals", "AIAA") {}
    uint256 AIAlienAnimalsPrice = 10000000000000000; // 0.01 ETH

    event NewAlien (
        uint256 tokenId,
        address owner,
        string tokenURI
    );
    
    function registerAIAA(address owner, string memory tokenURI)
        public 
        payable returns (uint256)
    {
       require(msg.value == AIAlienAnimalsPrice, "Ether value sent is incorrect");
        uint256 tokenId = totalSupply();
        _mint(owner, tokenId);
        _setTokenURI(tokenId, tokenURI);
        emit NewAlien(tokenId, owner, tokenURI);

        return tokenId;
    }

    
}
