import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

json_headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

file_headers = {
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

def convert_data_to_json(content):
    data = {"pinataOptions": {"cidVersion": 1}, "pinataContent": content}
    return json.dumps(data)

def pin_file_to_ipfs(data):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        files={'file': data},
        headers=file_headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def pin_json_to_ipfs(json):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=json,
        headers=json_headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

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
