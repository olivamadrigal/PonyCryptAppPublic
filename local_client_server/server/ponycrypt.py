########################################################################################################
# PonyCrypt Library: creates an album                                                                  #
# Team Boaz: Urian Lee, Sandhya Ramachandraiah, Mohana Gudur Valmiki, & Samira Carolina Oliva Madrigal #
########################################################################################################
from random import randrange
import sys
import os
import io
from cryptosteganography import CryptoSteganography
import json
import requests
import google_auth_oauthlib
import google_auth_httplib2
import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from google.auth.transport.requests import Request
import random
import time
from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import AsymmetricPadding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import secrets
import pytest
import pytest_html
from pathlib import Path
import shutil
import webbrowser
import base64
# from simple_aes_cipher import AESCipher
import pyaes
from stegano import lsb


class PonyCrypt:
    """
    PonyCrypt Client Script
    """

    def __init__(self):
        self.API_KEY = 'YOUR_API_KEY'
        self.CHATROOM_URL = 'https://photos.google.com/share/AF1QipMykwtfI9sbMOR43us4UXC0phk9HZEj4cIC0Sx7PsEf_iQuDYWPS6YOo28PGnOxUQ?key=d0pvb0wwUVFKdFFXN1d4dE0yNlZ6X1pldWxmazln'
        self.MAX_CHAT_ROOM = 1000
        self.MAX = 50    # client starts out with initial image repository
        self.CHATROOM = '17711'   # updated for subsequent generations and use create_chat_room
        self.START_COUNT = 17725  # 22ND fibonacci # FIRST CHAT ROOM
        self.THIS_PATH = os.path.dirname(os.path.realpath(__file__))
        self.PONIES = str(self.THIS_PATH) + "/PONIES/"  # STORE CHATS PER PONY
        self.CHATROOM_FILE = self.PONIES + "chatrooms.txt"  # STORE ALL ALBUMS album:id
        self.IMAGE_DIR = str(self.THIS_PATH) + "/images/"  # images to select from to encrypt
        self.CURRENT_PONY = self.PONIES + '/17711/'
        self.CRYPTO_IMG_DIR = self.CURRENT_PONY + "/outbox/"  # obscured & encrypted images are saved here
        self.DOWNLOADS = self.CURRENT_PONY + "/inbox/"  #downloads
        self.MEDIA_ID_FILE = self.CURRENT_PONY + "media.txt"  # list of all media ids for encrypted images
        self.SYMMETRIC_KEY_FILE = self.CURRENT_PONY + "key.txt"  # key file storing  symmetric key
        self.SYMMETRIC_KEY = None  # key used to encrypt after obscuring

        # RSA CLIENT PARAMETERS --- Public key Parameters -- to exchange public keys etc.
        self.RSA_PK = rsa.generate_private_key(public_exponent=257, key_size=2048, backend=default_backend())
        self.RSA_PU = self.RSA_PK.public_key()
        self.pad = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                algorithm=hashes.SHA256(), label=None)

        # KEX
        self.globals = dh.generate_parameters(generator=2, key_size=1024, backend=default_backend())
        self.DH_PK = self.globals.generate_private_key()
        self.DH_PU = self.DH_PK.public_key()
        self.DH_SHARED_SECRET = None
        self.PROCESSED_MEDIA_IDX = 0
        # self.CRYPTOSTEGO = None
        self.cs = None
        self.CIPHER = None
        self.CIPHER_KEY = "This_key_for_demo_purposes_only!"

    # MEDIA METADATA WITHIN A MEDIA OBJECT
    class MediaMetaData:
        """
        Media MetaData
        """
        def __init__(self, **kwargs):
            self.creationTime = None
            self.width = None
            self.height = None
            self.photo = None

    # WHEN WE UPLOAD A PHOTO STORES RETURNED OBJECT
    class NewMediaResults:
        """
        Object to hold response data
        """
        def __init__(self, **kwargs):
            self.id = None #NEW MEDIA ID
            self.description = None
            self.productUrl = None
            self.mimeType = None
            self.mediaMetadata = None
            self.contributorInfo = None
            self.filename = None
            self.__dict__.update(kwargs)

    # CREATE A MEDIA ITEM -- THIS HOLDS ALL INFORMATION FOR A PHOTO WITHIN AN ALBUM
    class MediaItem:
        """
        Object to hold media item details
        """
        def __init__(self, **kwargs):
            """
            Media Item Object
            """
            self.id = None
            self.description = None
            self.productUrl = None
            self.baseUrl = None
            self.mimeType = None
            self.mediaMetadata = None
            self.filename = None
            self.__dict__.update(kwargs)

    def generate_symmetric_key(self, new_pony=False):
        """
        Create Symmetric Key and Store in File -- THIS SECRET IS SHARES AMONG ALL NODES IN A CURRENT CHAT
        SECRET IS SHARED WITH EACH NODE: SERVER ENCRYPTS THE SECRET WITH THE CLIENTS PUBLIC KEY
        :param new_pony: flag is chatroom exists, if it is newly created key is generated else read from file
        """
        if new_pony: # IF THIS IS A NEW CHATROOM -- executed only by server or when testing this library
            self.SYMMETRIC_KEY = str(random.getrandbits(256))  # pseudo-random number generator
            fp = open(self.SYMMETRIC_KEY_FILE, "w")
            fp.write(self.SYMMETRIC_KEY)
            fp.close()
        else:  # when application is running
            fp = open(self.SYMMETRIC_KEY_FILE, "r")
            self.SYMMETRIC_KEY = fp.readline()
            fp.close()
        # OBJECT USED TO PERFOM CRYPTO & STEGANOGRAPHY
        # self.CRYPTOSTEGO = CryptoSteganography(self.SYMMETRIC_KEY)
        self.cs = CryptoSteganography(self.SYMMETRIC_KEY)

    def encode_pix(self, secret, img_name):
        """
        ENCODE SECRET INTO A MESSAGE & encrypt

        :param secret: secret message to encode
        :return: crypto image
        """
        # SELECT FILE AT RANDOM FROM SERVER'S IMAGE REPOSITORY
        file_name = "in" + str(randrange(1, self.MAX+1)) + ".png"
        input_img = self.IMAGE_DIR + file_name  # INTERNAL USE ONLY
        output_img = self.CRYPTO_IMG_DIR + img_name   # TO IDENTIFY A USER'S POST
        # TEST WTIH CRYPTOSTEGANO
        #cs = CryptoSteganography(self.SYMMETRIC_KEY)
        # Save the encrypted file inside the image
        self.cs.hide(input_img, output_img, secret)
        # TEST WITH STEGANO LIBRARY
        # sc = lsb.hide(input_img, secret)
        # sc.save(output_img)
        return output_img
        # return file_name, output_img

    def decode_pix(self, crypto_image_path):
        """
        DECRYPT MESSAGE & DECODE SECRET MESSAGE FROM IMAGE
        :return: secret in image
        """
        # CRYPTOSTEGANO
        secret = self.cs.retrieve(crypto_image_path)
        # secret = self.CRYPTOSTEGO.retrieve(crypto_image_path)
        # STEGANO
        # secret = lsb.reveal(crypto_image_path)
        return secret

    def upload_photo(self, access_token, file_path, file_name, albumId):
        """
        UPLOAD PHOTO TO EXISTING ALBUM
        
        :param access_token: access_token for session
        :param file_path: path of file
        :param file_name: file with hidden secret & encrypted file
        :return: status (used for verification test case), media_id (photo id for later processing)
        """
        url = 'https://photoslibrary.googleapis.com/v1/uploads'
        headers = {
            'Authorization': "Bearer " + access_token,
            'Content-Type': 'application/octet-stream',
            'X-Goog-Upload-File-Name': file_name,
            'X-Goog-Upload-Protocol': "raw",
            }
        upload_file = open(file_path, 'rb').read()
        returned_data = requests.post(url, headers=headers, data=upload_file)
        # print('\nUpload token: %s' % r.text)
        upload_token = returned_data.text

        url = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'
        headers = {
            'Authorization': "Bearer " + access_token,
            'Content-Type': 'application/json',
        }
        body = {
            "albumId": albumId,
            "newMediaItems": [
                {
                    "description": "~",
                    "simpleMediaItem": {
                        "fileName": file_name,
                        "uploadToken": upload_token
                    }
                }
            ]
        }
        payload = json.dumps(body)
        returned_data = requests.post(url, headers=headers, data=payload)
        new_media_info = returned_data.json()['newMediaItemResults'][0]['mediaItem']  # dictionary of new media
        # metadata = returned_data.json()['newMediaItemResults'][0]['mediaItem']['mediaMetadata'] # dict of metadat
        # md_obj = self.MediaMetaData(**metadata)
        # new_media_info['mediaMetadata'] = md_obj
        new_media_obj = self.NewMediaResults(**new_media_info)  # new media object
        return returned_data.status_code, new_media_obj

    def get_access_token(self):
        """
        Credential

        USES json credentials generated by Google to PonyCrypt for
        Google Photos API access

        :return: application OAUTH 2 access token
        """
        SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
                  'https://www.googleapis.com/auth/photoslibrary.appendonly',
                  'https://www.googleapis.com/auth/photoslibrary.sharing']
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        flow.run_local_server(port=0)
        access_token = flow.oauth2session._client.access_token
        return access_token

    def dh_kex_with_client(self, PU):
        """
        Diffie-Hellman Key Exchange
        :param client's dh PUBLIC KEY
        """
        self.DH_SHARED_SECRET = self.DH_PK.exchange(PU)

    def save_media(self, mediaId):
        """
        Save media ID

        :param album_name: album name
        :param mediaId: photo media id
        """
        fp = open(self.MEDIA_ID_FILE, "a")  # create album
        fp.write(str(mediaId) + "\n")  # save append album_name : album_id

    def download_photo(self, access_token, mediaId):
        """
        DOWNLOAD A MEDIA ITEM
        :param access_token: token to access the API
        :param album: album name
        :param mediaId: id of photo within album
        """
        headers = {
        'Authorization': "Bearer " + access_token,
        'Content-Type': 'application/json',
        }
        url = "https://photoslibrary.googleapis.com/v1/mediaItems/" + mediaId
        returned_data = requests.get(url, headers=headers)
        media_details = returned_data.json()
        # metadata = self.MediaMetaData(**media_details['mediaMetadata'])
        # media_details['mediaMetadata'] = metadata
        media_obj = self.MediaItem(**media_details)
        return returned_data.status_code, media_obj

    def send_message(self, message, access_token, albumId, img_name):
        """
        SEND CHATROOM MESSAGE
        """
        crypto_file_path = self.encode_pix(message, img_name)
        status_code, media_obj = self.upload_photo(access_token, crypto_file_path, img_name, albumId)
        self.save_media(media_obj.id)
        return status_code

    def get_message(self, access_token):
        """
        RECEIVED MEDIA
        """
        # GET MEDIA ID FROM FILE
        with open(self.MEDIA_ID_FILE, "r") as fp:
            media_lines = fp.readlines()
        media_items = [line.strip() for line in media_lines]
        mediaId = media_items[-1]
        # mediaId = media_items[self.PROCESSED_MEDIA_IDX]
        # self.PROCESSED_MEDIA_IDX = self.PROCESSED_MEDIA_IDX + 1
        # DOWNLOAD THE FILE
        status_code, media_obj = self.download_photo(access_token, mediaId)
        resp = requests.get(media_obj.baseUrl, stream=True)
        local_file = open(self.DOWNLOADS + media_obj.filename, 'wb')
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, local_file)
        secret = self.decode_pix(local_file.name)
        fp = open(self.THIS_PATH + '/secrets.txt', 'a')
        fp.write(secret + '\n')
        fp.close()
        return secret
        # return status_code, secret, media_obj.filename
    
    def get_chat_room_id(self, specify=False):
        """
        GET ALBUM ID for this PONY
        :param specify chatroom name
        :return chat room name, chat room id
        """
        with open(self.CHATROOM_FILE, "r") as fp:
            rooms = fp.readlines()
        room_list = [x.rstrip() for x in rooms]

        if len(room_list) == 1:
            toks = room_list[0].split(':')

        if not specify:
            # get most recent pony
            most_recent = room_list[-1]
            toks = most_recent.split(':')
        else:
            for room in room_list:
                if self.CHATROOM in room:
                    toks = room.split(':')
                    break
        return toks[0], toks[1] #chat_name, chat_id

    def get_most_recent_chatroom(self):
        """
        GET START POINT
        NOTE: TO RUN TEST SCRIPT MUST MODIFY THIS MANUALLY
        OTHERWISE WILL ERROR OUT:
        "pytest: reading from stdin while output is captured!  Consider using `-s`."
        This is fine with -s, but not when trying to capture output to LOGS
        """
        chatroom = input("Enter most recent chat room #:")
        return int(chatroom)

    def create_chat_room(self):
        """
        CREATE A CHATROOM
        """
        # NOTE: TO RUN TEST SCRIPT COMMENT OUT self.START_COUNT & INPUT MANUALLY
        # OTHERWISE WILL ERROR OUT:
        #         "pytest: reading from stdin while output is captured!  Consider using `-s`."
        # This is fine with -s, but not when trying to capture output to LOGS

        #self.START_COUNT = self.get_most_recent_chatroom()
        # CREATE A NEW PONY
        self.START_COUNT = self.START_COUNT + 1  # UPDATE MANUALLY WHEN TESTING
        self.CHATROOM = str(self.START_COUNT)
        self.CURRENT_PONY = self.PONIES + self.CHATROOM + "/"
        os.mkdir(self.CURRENT_PONY)  # a new pony
        self.CRYPTO_IMG_DIR = self.CURRENT_PONY + "outbox" + "/"
        os.mkdir(self.CRYPTO_IMG_DIR)  # crypto image dir
        self.DOWNLOADS = self.CURRENT_PONY + "inbox" + "/"
        os.mkdir(self.DOWNLOADS)  # inbox dir for downloads
        self.MEDIA_ID_FILE = self.CURRENT_PONY + "media.txt"
        Path(self.MEDIA_ID_FILE).touch()
        self.SYMMETRIC_KEY_FILE = self.CURRENT_PONY + "key.txt"
        Path(self.SYMMETRIC_KEY_FILE).touch()

    def get_access_token(self):
        """
        Credential
        
        USES json credentials generated by Google to PonyCrypt for
        Google Photos API access
        
        :return: application OAUTH 2 access token
        """
        SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
                  'https://www.googleapis.com/auth/photoslibrary.appendonly',
                  'https://www.googleapis.com/auth/photoslibrary.sharing']
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        flow.run_local_server(port=0)
        access_token = flow.oauth2session._client.access_token
        return access_token

    class AlbumItem:
        """
        ALBUM ID
        """
        def __init__(self, **kwargs):
            self.id = None
            self.title = None
            self.productUrl = None
            self.isWriteable = None
            self.__dict__.update(kwargs)

    def create_album(self, album_name, access_token):
        """
        Create an album to store crypto images
        :return: the  status_code & album object
        """
        body = {"album": {"title": album_name}}
        headers = {'Authorization': "Bearer " + access_token,
                   'Content-Type': 'application/json',
                  }
        url = 'https://photoslibrary.googleapis.com/v1/albums'
        returned_data = requests.post(url, headers=headers, data=json.dumps(body))
        output = returned_data.json()
        album_obj = self.AlbumItem(**output)
        self.save_album(album_obj.id)  # FOR PROCESSING MEDIA ITEM LATER
        return returned_data.status_code, album_obj

    class SharedAlbum:
        """
        SHARED ALBUM OBJECT
        """
        def __init__(self, **kwargs):
            self.sharedAlbumOptions = None  # dictionary {'isCollaborative': True}
            self.shareableUrl = None
            self.shareToken = None
            self.isJoined = None
            self.isOwned = None
            self.__dict__.update(kwargs)
        
    def share_album(self, albumId, access_token):
        """
        SHARE PONYCRYPT ALBUM
        """
        body = {
            "sharedAlbumOptions": {
                "isCollaborative": 'true',
                "isCommentable": 'false'}
        }
        headers = {
        'Authorization': "Bearer " + access_token,
        'Content-Type': 'application/json'
        }
        url = 'https://photoslibrary.googleapis.com/v1/albums/' + albumId + ':share'
        returned_data = requests.post(url, headers=headers, data=json.dumps(body))
        output = returned_data.json()
        sharedInfo = output['shareInfo']
        shared_album_obj = self.SharedAlbum(**sharedInfo)
        return returned_data.status_code, shared_album_obj

    def save_album(self, albumId):
        """
        Save album id
        
        :param album_name: album name
        :param album_id: album id
        """
        fp = open(self.CHATROOM_FILE, "a")  # create album
        fp.write(self.CHATROOM + ":" + albumId + "\n")  # save append album_name : album_id

    def print_test_data(self, description, data):
        """
        PRINT DATA
        """
        print(description + data)
