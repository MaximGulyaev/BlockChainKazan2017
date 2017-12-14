import rsa
import hashlib
import base64
import consts

class CAccountingSystem:
    account = {
        'Name': None,
        'PublicKey': None,
        'PrivateKey': None,
        'Address': None,
        'Organization': None,
        'Birthday': None,
        'isExpert': None,
    }

    isAuthorized = False
    mineClass = None
    dataBaseAdapt = None

    def __init__(self, DBA):
        self.dataBaseAdapt = DBA
        return None

    def authorization(self, PrivateKey):
        user = self.dataBaseAdapt.getUser(self.publicKeyToAddress(PrivateKey))
        if (user == None):
            self.logout()
            return False
        self.isAuthorized = True
        self.account['PrivateKey'] = PrivateKey
        self.account['PublicKey'] = self.privateKeyToPublic(PrivateKey)
        self.account['Address'] = self.publicKeyToAddress(PrivateKey)
        self.account['Organization'] = user[consts.usersColumns.get('organization')]
        self.account['Birthday'] =  user[consts.usersColumns.get('birthday')]
        self.account['Name'] = user[consts.usersColumns.get('name')]
        self.account['isExpert'] = user[consts.usersColumns.get('isExpert')]
        return True

    def logout(self):
        self.isAuthorized = False
        self.account['PrivateKey'] = None
        self.account['PublicKey'] = None
        self.account['Address'] = None
        self.account['Organization'] = None
        self.account['Birthday'] = None
        return True

    def isAuthorizedUserExpert(self):
        # getisExpert(self.account['Address'])
        return True

    @staticmethod
    def generateKey():
        (pubkey, privkey) = rsa.newkeys(1024)
        return(privkey)

    @staticmethod
    def privateKeyToPublic(PrivateKey):
        PublicKey = rsa.PublicKey(PrivateKey.n, PrivateKey.e)
        return(PublicKey)

    @staticmethod
    def publicKeyToString(PublicKey):
        PublicKeyString = str(PublicKey.n).encode()
        PublicKeyString = PublicKeyString + b', ' + str(PublicKey.e).encode()
        return(PublicKeyString.decode())

    @staticmethod
    def stringToPublicKey(string):
        if type(string) != str:
            string = string.decode()
        n = int(string[:string.find(',')])
        e = int(string[string.find(' '):])
        PublicKey = rsa.PublicKey(n,e)
        return(PublicKey)


    @staticmethod
    def publicKeyToAddress(PublicKey):
        PublicKeyString = str(PublicKey.n).encode()
        PublicKeyString = PublicKeyString + str(PublicKey.e).encode()
        Address = str(base64.b64encode(hashlib.sha256(PublicKeyString).digest()))[2:-2]
        return(Address)

    @staticmethod
    def createSingature(privateKey, string):
        if type(string) == str:
            string = string.encode()
        s = rsa.sign(string, privateKey, 'SHA-256')
        return (s.hex())


    @staticmethod
    def checkSignature(PublicKey, string, signature):
        try:
            if type(string) == str:
                string = string.encode()
            signature = bytes.fromhex(signature)
            s = rsa.verify(string, signature, PublicKey)
            return(s)
        except rsa.pkcs1.VerificationError:
            return False






(pubkey, privkey) = rsa.newkeys(1024)
CAccountingSystem.privateKeyToPublic(privkey)


