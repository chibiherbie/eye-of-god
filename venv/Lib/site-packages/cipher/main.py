import base64
from .constant import CIPHER_DICT


class Cipher(object):

    def __init__(self):
        self.encrypt_dict = CIPHER_DICT
        self.decrypt_dict = dict((v, k) for k, v in CIPHER_DICT.items())

    def encrypt(self, sentence):
        ciphertext = ''
        sentence = sentence.encode("utf8")
        base64_sentence = base64.b64encode(sentence)
        base64_sentence = base64_sentence.decode("utf8")
        for i in base64_sentence:
            j = self.encrypt_dict[i]
            ciphertext += j
        return ciphertext

    def decrypt(self, ciphertext):
        plaintext = ''
        for i in ciphertext:
            j = self.decrypt_dict[i]
            plaintext += j
        plaintext = base64.b64decode(plaintext)
        plaintext = plaintext.decode("utf8")
        return plaintext
