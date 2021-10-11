from ponycrypt import *
from ponycrypt_test_base import *
import pytest
import pytest_html


class TestPonyCrypt(PonyCryptTestBase):
    """
    PonyCrypt API TEST CASE

    MODIFY THESE TWO ATTRIBUTES AS YOUR WISH TO RUN YOUR TEST.

    self.test_secret = 'hi how are you?'  # KEEP IT SMALL & ALL ASCII CHARS
    self.test_img_name = 'unicorns.png'   # KEEP IT REASONABLE
    """
    def setup_class(self):
        """
        SET UP - RUNS ONCE PER EXECUTION
        """
        self.pony = PonyCrypt()
        self.access_token = self.pony.get_access_token()  # FLOW CREDENTIALS
        self.test_secret = 'hello?'
        self.test_img_name = 'unicorns.png'
        self.pony.create_chat_room()
        self.pony.generate_symmetric_key(new_pony=True)
        self.ALBUM_ID_FILE = 'album_id.txt'
        Path(self.ALBUM_ID_FILE).touch()
        self.MEDIA_ID_FILE = 'media_id.txt'
        Path(self.MEDIA_ID_FILE).touch()
        self.MEDIA_BASEURL = 'media_url.txt'
        Path(self.MEDIA_BASEURL).touch()

    def test_goole_create_album_api(self):
        """
        TEST Google Create Album
        """
        status_code, album_obj = self.pony.create_album(self.pony.CHATROOM, self.access_token)
        kwargs = {'title': self.pony.CHATROOM,
                  'productUrl': ('https://photos.google.com/lr/album/' + album_obj.id),
                  'isWriteable': True}
        expected = self.pony.AlbumItem(**kwargs)
        self.verify_create_new_album(status_code, album_obj, expected, kwargs)
        self.save_data(self.ALBUM_ID_FILE, album_obj.id)
        print(vars(album_obj))

    def test_google_share_album_api(self):
        """
        TEST Google Share Album
        """
        album_id = self.get_data(self.ALBUM_ID_FILE)
        status_code, shared_album_obj = self.pony.share_album(album_id, self.access_token)
        kwargs = {'isJoined': True, 'isOwned': True}
        expected = self.pony.SharedAlbum(**kwargs)
        self.verify_shared_album(status_code, shared_album_obj, expected, kwargs)
        print(vars(shared_album_obj))


    def test_google_post_api(self):
        """
        TEST Google REST POST API
        """
        album_id = self.get_data(self.ALBUM_ID_FILE)
        crypto_file_path = self.pony.encode_pix(self.test_secret, self.test_img_name)
        status_code, new_media_obj = self.pony.upload_photo(self.access_token,
                                                            crypto_file_path,
                                                            self.test_img_name,
                                                            album_id)
        kwargs = {'description': '~',
                  'productUrl': 'https://photos.google.com/lr/album/' + album_id + '/photo/' + new_media_obj.id,
                  'filename': self.test_img_name
        }
        expected = self.pony.NewMediaResults(**kwargs)
        self.verify_post_api(status_code, new_media_obj, expected, kwargs)
        self.save_data(self.MEDIA_ID_FILE, new_media_obj.id)  # SET THIS FOR NEXT TEST
        self.pony.save_media(new_media_obj.id)
        print(vars(new_media_obj))

    def test_google_get_api(self):
        """
        TEST Google REST POST API
        """

        media_id = self.get_data(self.MEDIA_ID_FILE)
        status_code, media_obj = self.pony.download_photo(self.access_token, media_id)
        kwargs = {'id': media_id,
                  'description': '~',
                  'productUrl': 'https://photos.google.com/lr/photo/' + media_id,
                  'filename': self.test_img_name}
        expected = self.pony.MediaItem(**kwargs)
        self.verify_get_api(status_code, media_obj, expected, kwargs)
        self.save_data(self.MEDIA_BASEURL, media_obj.baseUrl) # FOR NEXT TEST CASE
        print(vars(media_obj))


    def test_cryptosteganography(self):
        """
        TEST CRYPTOSTEGANOGRAPHY
        """
        media_baseUrl = self.get_data(self.MEDIA_BASEURL)
        resp = requests.get(media_baseUrl, stream=True)
        assert resp.status_code == 200
        local_file = open(self.pony.DOWNLOADS + self.test_img_name, 'wb')
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, local_file)
        secret = self.pony.decode_pix(local_file.name)
        assert secret == self.test_secret  # CRYPTO STEGO SUCCESSFUL
        print(secret + "==" + self.test_secret)

    # @pytest.mark.parametrize("test_vector", [PonyCryptTestBase.get_secret_test_vector()])
    def test_post_get_crypto(self):#, test_vector):
        """
        TO LOOP THE PREVIOUS TEST CASES MUST BE INTEGRATED
        USING SAME ALBUM, WE POST AND GET REPEATEDLY USING ENCODING & DECODING DIFFERENT MESSAGES
        """
        self.generate_tb_file()
        test_vector = self.get_secret_test_vector()
        album_id = self.get_data(self.ALBUM_ID_FILE)
        for filename, expected_secret in test_vector.items():
            # ENCODE
            crypto_file_path = self.pony.encode_pix(expected_secret, filename)
            # UPLOAD
            status_code, new_media_obj = self.pony.upload_photo(self.access_token,
                                                                crypto_file_path,
                                                                filename,
                                                                album_id)
            kwargs = {'description': '~',
                  'productUrl': 'https://photos.google.com/lr/album/' + album_id + '/photo/' + new_media_obj.id,
                  'filename': filename
            }
            expected = self.pony.NewMediaResults(**kwargs)
            self.verify_post_api(status_code, new_media_obj, expected, kwargs)
            # DOWNLOAD
            status_code, media_obj = self.pony.download_photo(self.access_token, new_media_obj.id)
            kwargs = {'id': new_media_obj.id,
                  'description': '~',
                  'productUrl': 'https://photos.google.com/lr/photo/' + new_media_obj.id,
                  'filename': filename}
            expected = self.pony.MediaItem(**kwargs)
            self.verify_get_api(status_code, media_obj, expected, kwargs)
            # RECONSTRUCT & DECODE
            resp = requests.get(media_obj.baseUrl, stream=True)
            assert resp.status_code == 200
            local_file = open(self.pony.DOWNLOADS + filename, 'wb')
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, local_file)
            actual_secret = self.pony.decode_pix(local_file.name)
            assert actual_secret == expected_secret  # CRYPTO STEGO SUCCESSFUL
            print(actual_secret + "==" + expected_secret)
