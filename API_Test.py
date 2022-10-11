import requests
import json
import streamlit as st
import getpass
import io
import os
import warnings
from PIL import Image

# If 'pip install stability-sdk' has errors try 'pip install stability-sdk --user':
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from dotenv import load_dotenv

load_dotenv()

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

generate_button = st.button("Generate")

if generate_button:

    # The object returned is a python generator:
    answers = stability_api.generate(
        prompt="A cute alien animal." 
    )

    # Iterating over the generator produces the api response:
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                st.image(img)

    # Getting the attributes:
    job_title_request = requests.get(job_title_url)
    job_title = job_title_request.json()

    planet_request = requests.get(planet_url)
    planet = planet_request.json()

    alien_request = requests.get(alien_url)
    alien = alien_request.json()

    language_request = requests.get(language_url)
    language = language_request.json()

    teleportation_request = requests.get(teleportation_url)
    teleportation = teleportation_request.json()

    st.write(f"Name: {alien.capitalize()}")
    st.write(f"Description: {job_title}")
    st.write(f"Planet: {planet}")
    st.write(f"Language: {language.capitalize()}")
    st.write(f"Teleportation: {teleportation}")



