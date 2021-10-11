import random
import string


class PonyCryptTestBase:

    input_tb = 'input_tb.txt'
    trials = 'trials.txt'

    def get_trials(self):
        """
        trials file
        """
        fp = open(self.trials, "r")
        trials = fp.readline()
        return int(trials)

    def generate_tb_file(self):
        """
        generate test data
        """
        trials = self.get_trials()
        prefix = 'test_pix'
        a = 1
        b = 3
        fp = open(self.input_tb, "w")
        for i in range(0, trials):
            filename = prefix + str(i) + '.png'
            # secret = str(a) + '+' + str(b) + '=' + str(a + b)
            secret = ''.join(random.choice(string.ascii_letters) for _ in range(10))
            a = a + 1
            b = b + 1
            tb = filename + ':' + secret + '\n'
            fp.write(tb)

    def get_secret_test_vector(self):
        """
        return secrets file
        :param tb_file: TB FILE
        """
        file_secret_dict = {}
        fp = open(self.input_tb, "r")
        lines = fp.readlines()
        for line in lines:
            line = line.rstrip()
            tokens = line.split(':')
            file_secret_dict[tokens[0]] = tokens[1]
        return file_secret_dict

    def save_data(self, file_name, data):
        """
        SAVE DATA NEEDED FOR OTHER TEST CASES
        (calls between test cases clears globals)
        :param file_name: FILE NAME
        :param data: data to save
        :return:
        """
        fp = open(file_name, "w")
        fp.write(data)
        fp.close()

    def get_data(self, file_name):
        """
        GET DATA NEEDED FOR OTHER TEST CASES
        (calls between test cases clears globals)
        :param file_name: FILE NAME
        :return: data
        """
        fp = open(file_name, "r")
        data = fp.readline()
        fp.close()
        return data

    def compare_attributes(self, keys, actual, expected):
        """
        COMPARE TWO OBJECTS FOR EQUALITY OF KEYS
        :param keys: keys to compare
        :param actual: actual object
        :param expected: expected object
        """
        for key in keys:
            assert getattr(actual, key) == getattr(expected, key)

    def verify_create_new_album(self, status_code, actual, expected, kwargs):
        """"
        verify create new album
        :param status_code: POST request status code
        :param actual: actual AlbumItem obj
        :param expected: expected AlbumItem object
        :param kwargs:  dict with keys to compare for equality
        """
        assert status_code == 200    # RETURNED OK
        self.compare_attributes(kwargs.keys(), actual, expected)
        assert actual.id  # NOT NIL

    def verify_shared_album(self, status_code, actual, expected, kwargs):
        """
        verify shared album obj
        :param status_code: POST request status code
        :param actual: actual SharedAlbum obj
        :param expected: expected SharedAlbum obj
        :param kwargs:  dict with keys to compare for equality
        """
        assert status_code == 200
        self.compare_attributes(kwargs.keys(), actual, expected)
        assert actual.sharedAlbumOptions['isCollaborative'] == True
        assert 'https://photos.app.goo.gl' in actual.shareableUrl
        assert actual.shareToken  # NOT NIL

    def verify_post_api(self, status_code, actual, expected, kwargs):
        """
        verify post api
        :param status_code: POST request status code
        :param actual: actual SharedAlbum obj
        :param expected: expected SharedAlbum obj
        :param kwargs:  dict with keys to compare for equality
        """
        assert status_code == 200
        self.compare_attributes(kwargs.keys(), expected, actual)
        assert actual.id  # NEW MEDIA ID
        assert 'image' in actual.mimeType
        assert actual.mediaMetadata

    def verify_get_api(self, status_code, actual, expected, kwargs):
        """
        verify get apI
        :param status_code: POST request status code
        :param actual: actual MediaItem obj
        :param expected: expected MediaItem obj
        :param kwargs: dict with keys to compare for equality
        """
        assert status_code == 200
        self.compare_attributes(kwargs.keys(), expected, actual)
        assert 'https://lh3.googleusercontent.com/lr/' in actual.baseUrl
        assert 'image' in actual.mimeType
        assert actual.mediaMetadata  # NOT NIL
