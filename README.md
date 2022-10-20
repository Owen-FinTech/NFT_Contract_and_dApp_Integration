# NFT_Contract_and_dApp_Integration

## Project Overview:

This project aims to build an AI generated NFT collection in which the user can select their wallet, generate a mintable NFT that is AI generated and contains AI generated attributes such as a job title, home planet, name, language and skill specific to the ‘Alien Animal’ the user receives.

Once the NFT has been generated the user can then mint the NFT for the price of 0.01 ETH plus associated gas fees which will then be stored in their wallet.

Within the application the user can visualise the ‘Alien Animals’ they already hold within their selected wallet.

## Project Breakdown:

### Contract (contract.sol):

Utilises Solidty (Pragma Solidity 0.5.5) and has been compiled using Brownie.

### App.py and Pinata.py:

Pulls in AI generated attributes for the NFT via APIs connected to generatorfun.com. This gives our AI generated images called ‘Alien Animals’ attributes including a job title, home planet, name, language and skill specific to the alien animal.

The image/art work for the NFT is also AI generated and is pulled using Stability API image generator.

The application is run through Streamlit and the attributes and image data are held while the application is interacted with using the session state tool. 

While interacting with the Streamlit application the user can select their wallet via the ‘Select Your account” drop down.

![aiaa_lauch_screen](https://user-images.githubusercontent.com/103994978/196907191-e825849b-aff1-4c76-bda9-f74554f539f6.png)

They can then generate a mintable NFT artwork by clicking the “Generate New NFT Preview” button. Upon clicking this button, the Stability API will generate an artwork and the APIs linked to generatorfun.com will produce a series of attributes for the NFT. This image is then collated in a file and pinned to IPFS with Pinata, the attributes are compiled into a metadata JSON file and pinned to IPFS with Pinata.

![aiaa_preview](https://user-images.githubusercontent.com/103994978/196907632-1630317c-9f06-457f-a60a-615537f179df.png)

Once happy with their generated artwork the user can then mint the NFT by clicking the “Mint This NFT (0.01 ETH + Gas)” button which will mint the NFT into the users wallet and charge the user 0.01 ETH for the ‘Alien Animal’ and an additional charge for the associated gas fees.

The user can visualise all ‘Alien Animals’ currently in their wallet by interacting with the side bar “View Minted NFTs”. The user can select their chosen wallet via the “Select Account…” drop down and can generate thumbnail of their held NFTs by clicking the “Display NFT’s linked to this address” button.

![view_minted_nfts](https://user-images.githubusercontent.com/103994978/196907862-6af4b883-9467-45ee-a44f-13a1085e9141.png)

