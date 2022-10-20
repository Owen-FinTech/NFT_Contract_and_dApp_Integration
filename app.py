import requests
import json
import streamlit as st
import io
import os
import warnings
from PIL import Image
from pathlib import Path
from web3 import Web3

## Importing functions:
from pinata import convert_data_to_json, pin_file_to_ipfs, pin_json_to_ipfs

# If 'pip install stability-sdk' has errors try 'pip install stability-sdk --user':
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from dotenv import load_dotenv

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Load_Contract Function
@st.cache(allow_output_mutation=True)
def load_contract():

    # Load the contract ABI
    with open(Path('contracts/compiled/contract_abi.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract


# Load the contract
contract = load_contract()

# Job title, planet name, alien name, language name & teleportation name APIs:
job_title_url = os.getenv("JOB_TITLE_URL") 
planet_url = os.getenv("PLANET_URL")
alien_url = os.getenv("ALIEN_URL")
language_url = os.getenv("LANGUAGE_URL")
teleportation_url = os.getenv("TELEPORTATION_URL")

# Stability API image generator access:
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = os.getenv("STABILITY_SECRET_KEY")

stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'], 
    verbose=True,
)


# Heading:
st.markdown("# AI Alien Animal NFT Generator")

def states():
    # Initializing session states:
    st.session_state.alien = None
    st.session_state.img_byte_arr = None
    st.session_state.job_title = None
    st.session_state.planet = None
    st.session_state.language = None
    st.session_state.teleportation = None
    st.session_state.the_image = None
    st.session_state.receipt = None
    st.session_state.artwork_ipfs_hash = None
    st.session_state.token_json = None
    st.session_state.resp = None
    st.session_state.answers = None
    st.session_state.artifact = None
    
def generate_alien():
    # The object returned is a python generator:
    st.session_state.answers = stability_api.generate(
        prompt="A cute alien animal." 
    )

    # Iterating over the generator produces the api response:
    for st.session_state.resp in st.session_state.answers:
        for st.session_state.artifact in st.session_state.resp.artifacts:
            if st.session_state.artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if st.session_state.artifact.type == generation.ARTIFACT_IMAGE:
                st.session_state.the_image = Image.open(io.BytesIO(st.session_state.artifact.binary))

                # Saving the image:                    
                st.session_state.the_image.save('result.png')

                # Saving instance of image as bytes-like object:
                st.session_state.img_byte_arr = io.BytesIO(st.session_state.artifact.binary)
    
    return st.session_state.img_byte_arr, st.session_state.the_image

def get_attributes():
    # Getting the attributes: 
    # Title and strip ensures capitalization and no trailing spaces:
    job_title_request = requests.get(job_title_url)
    job_title = job_title_request.json()
    st.session_state.job_title = job_title.title().strip()

    planet_request = requests.get(planet_url)
    planet = planet_request.json()
    st.session_state.planet = planet.title().strip()

    alien_request = requests.get(alien_url)
    alien = alien_request.json()
    st.session_state.alien = alien.title().strip()

    language_request = requests.get(language_url)
    language = language_request.json()
    st.session_state.language = language.title().strip()

    teleportation_request = requests.get(teleportation_url)
    teleportation = teleportation_request.json()
    st.session_state.teleportation = teleportation.title().strip()

    return st.session_state.job_title, st.session_state.planet, st.session_state.alien, st.session_state.language, st.session_state.teleportation

# Helper functions to pin files and json to Pinata
def pin_artwork(alien, img_byte_arr, job_title, planet, language, teleportation):
    
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(img_byte_arr.getvalue())

    # Build a token metadata file for the artwork
    token_json = {
        "name": alien,
        "description": job_title,
        "image": ipfs_file_hash,
        "attributes": [
            {
            "trait_type": "Planet", 
            "value": planet
            }, 
            {
            "trait_type": "Language", 
            "value": language
            }, 
            {
            "trait_type": "Teleportation", 
            "value": teleportation
            }]}
    json_data = convert_data_to_json(token_json)

    # Pin the json to IPFS with Pinata
    json_ipfs_hash = pin_json_to_ipfs(json_data)

    return json_ipfs_hash, token_json

def minting():
    # Use the `pin_artwork` helper function to pin the file to IPFS
    st.session_state.artwork_ipfs_hash, st.session_state.token_json = pin_artwork(
        st.session_state.alien, st.session_state.img_byte_arr, 
        st.session_state.job_title, st.session_state.planet,
        st.session_state.language, st.session_state.teleportation)

    artwork_uri = f"ipfs://{st.session_state.artwork_ipfs_hash}"

    # Build transaction with the registerAIAA function from our contract:
    tx = contract.functions.registerAIAA(
        Web3.toChecksumAddress(st.session_state.account),
        artwork_uri
    ).buildTransaction({'from': st.session_state.account, 'gas': 1000000, 'value': 10000000000000000, 'nonce': w3.eth.get_transaction_count(st.session_state.account)})
    
    # Signing the transaction, sending the raw transaction and getting the receipt:
    signed_txn = w3.eth.account.signTransaction(tx, private_key = st.session_state.key)
    ret = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    st.session_state.receipt = w3.eth.waitForTransactionReceipt(ret)

# Preloading 3 accounts that have Goerli test ETH on them:
accounts = ('0x8683d05977d6294784ca1C0aBBEc343ceccFb249', '0x98C56F45e6eF9b6a497367BAb18BA068e40642aB', '0xeC25944b7CCa67D883f92BDDCfBd2B888670ae66')

# Selecting the account:
st.session_state.account = st.selectbox("Select Account:", options = accounts)

# Associating private key with each account selected:
if st.session_state.account == '0x8683d05977d6294784ca1C0aBBEc343ceccFb249':
    st.session_state.key = os.getenv("KEY_1")
elif st.session_state.account == '0x98C56F45e6eF9b6a497367BAb18BA068e40642aB':
    st.session_state.key = os.getenv("KEY_2")
else:
    st.session_state.key = os.getenv("KEY_3")

# Generate button:
generate_button = st.button("Generate New NFT Preview")

# Mint button:
mint_nft = st.button("Mint This NFT (0.01 ETH + Gas)")

if generate_button:
    states()
    generate_alien()
    st.image('result.png')
    get_attributes()
    st.write(f"Name: {st.session_state.alien}")
    st.write(f"Description: {st.session_state.job_title}")
    st.write(f"Planet: {st.session_state.planet}")
    st.write(f"Language: {st.session_state.language}")
    st.write(f"Teleportation: {st.session_state.teleportation}")

if mint_nft: 
    st.image('result.png')
    st.write(f"Name: {st.session_state.alien}")
    st.write(f"Description: {st.session_state.job_title}")
    st.write(f"Planet: {st.session_state.planet}")
    st.write(f"Language: {st.session_state.language}")
    st.write(f"Teleportation: {st.session_state.teleportation}")
    minting()    
    st.markdown("## Transaction Receipt:")
    st.write(dict(st.session_state.receipt))
    st.write("You can view the pinned metadata file with the following IPFS Gateway Link:")
    st.markdown(f"[Artwork IPFS Gateway Link](https://gateway.pinata.cloud/ipfs/{st.session_state.artwork_ipfs_hash})")
    st.markdown(f"[Artwork IPFS Image Link](https://gateway.pinata.cloud/ipfs/{st.session_state.token_json['image']})")


# Collect active wallet addresses from smart contract
all_owners = []
owner_filter = contract.events.NewAlien.createFilter(fromBlock=0)
owners = owner_filter.get_all_entries()
if owners:
    for owner in owners:
        owner_dictionary = dict(owner)
        all_owners += [owner_dictionary['args']['owner']]
all_owners = set(all_owners)

# Streamlit sidebar
with st.sidebar:
    st.title("View Minted NFTs")
    option = st.selectbox('Select Account...', list(all_owners))
    if st.button("Display NFT's linked to this address"):
        account_filter = contract.events.NewAlien.createFilter(
            fromBlock=0, 
            argument_filters={'owner':Web3.toChecksumAddress(option).lower()}
        )
        tokens = account_filter.get_all_entries()
        if tokens:
            for token in tokens:
                token_dictionary = dict(token)
                token_URI = token_dictionary['args']['tokenURI']
                url = f'https://gateway.pinata.cloud/ipfs/{token_URI[7:]}'
                response_data = requests.get(url)
                reponse_content = response_data.content
                data = response_data.json()
                image_hash = data["image"]
                st.image(f'https://gateway.pinata.cloud/ipfs/{image_hash}')
        else:
            st.write("This account owns no tokens")
        
        









