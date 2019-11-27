import os
import requests


def download_file_from_google_drive(destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://drive.google.com/uc?authuser=0&id=1lDV0vQH2vVANRNorOBBSNToDCBaa0vM0&export=download"

    session = requests.Session()

    response = session.get(URL, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def download():
    path = os.path.abspath(os.path.dirname(__file__))
    download_file_from_google_drive(path + "/resources/frozen_east_text_detection.pb")

