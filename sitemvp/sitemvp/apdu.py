"""
Wrapper for GlobalPlatformPro
"""
from collections.abc import Iterable

from smartcard.System import readers
from smartcard.CardMonitoring import CardObserver
from smartcard.CardType import AnyCardType, CardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes

import cryptography
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives import padding, serialization

class CryptoWrapper:
    def generateRSAKeyPair(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
    def setAESKey(self, key):
        self.session_key = AES(key)
    def setCardRSAKey(self, key):
        self.card_key = rsa.RSAPublicKey

class CommandAPDU:
    getVersionIns            = 4
    sendPublicKeyIns         = 5
    receivePublicKeyIns      = 6
    returnDecryptedNonceIns  = 7
    sendEncryptedNonceIns    = 8
    receiveDecryptedNonceIns = 10
    getPinTriesRemainingIns  = 11
    tryPinIns                = 12
    sendSessionKeyIns        = 13
    testSessionKeyIns        = 14

    def __init__(self, raw: bytearray):
        self.buffer = bytearray
    def __init__(self, type:int = 0, instruction:int = getVersionIns, P1:int = 0, P2:int = 0, data=[]):
        if not isinstance(data, Iterable):
            data = [data]
        self.buffer = bytes([type, instruction, P1, P2]) + bytes(data)
        
class ResponseAPDU:
    def __init__(self, SW1, SW2, data=[]):
        self.SW = bytes([SW1, SW2])
        self.data = toBytes(data)

    def getSW(self):
        return self.SW

    def getData(self):
        return self.data

class Session:
    def __init__(self, cardType: CardType = AnyCardType()):
        cardrequest         = CardRequest(timeout=1, cardType=cardType)
        self.cardservice    = cardrequest.waitforcard()
        self.cardservice.connection.connect()

    def transmit(self, commandAPDU: CommandAPDU)->ResponseAPDU:
        apdu = commandAPDU.buffer
        response, sw1, sw2 = self.cardservice.connection.transmit(apdu)
        return ResponseAPDU(sw1, sw2, response)

    def tryPin(self, pin):
        command = CommandAPDU(instruction=CommandAPDU.tryPinIns, data=bytes(pin))
        response = self.transmit(command)

        command = CommandAPDU(instruction=CommandAPDU.getPinTriesRemainingIns)
        response = self.transmit(command)
        return response.getData() == 3

    def exchangePublicKeys(self):
        pass

    def exchangeSessionKey(self):
        pass

class CardObserver(CardObserver):
    def __init__(self):
        self.active = None

    def update(self, observable, actions):
        added, removed = actions
        if removed and self.active == removed[0]:
            del self.active
            self.active = None
        elif added and self.active is None:
            self.active = added[0]