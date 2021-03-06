import dataBaseAdapter
import CAccountingSystem
import network
import consts
import json
import hashlib
import time
import json
import copy
from collections import OrderedDict

Complexity = {
    "user": "000",
    "expert": "000",
}


class Blockchain:

    PrivateKey = 0
    dataBaseAdapt = dataBaseAdapter.dataBaseAdapter()
    CNetwork = None
    exitsChangeEventVresion = []
    _MineStat = 0
    _ReloadFunction = None

    def __init__(self):
        pass

    '''
    TransactionDict = {
        'address': ,
        'type':,
        'data':,
        'publicKey':,
        'signature':,

    }

    type ==
    0 - регистрация
    1 - повышение
    2 - разжалование
    3 - подтверждение разжалования/повышения
    4 - подтверждение редактирвоания события
    5 - создание события
    6 - редактирование события

    '''

    def setPrivateKey(self, PrivateKey):
        self.PrivateKey = PrivateKey

    def InitAddNetWork(self, NetClass):
        self.CNetwork = NetClass
        return True
    def InitAddFunction(self, Reload):
        self._ReloadFunction = Reload

    def addNewTransactFromNet(self, Transact):
        try:
            if self.transactionVerification(Transact):
                self.addTransactToUncTransact(Transact)
                return True

        except Exception as e:
            print (e)
            return False

    def addNewTransactFromUser(self, Transact):
        if self.transactionVerification(Transact):
            if (self.addTransactToUncTransact(Transact)):
                self.sendTransact(Transact)
                return True
        else:
            return False

    def addNewBlockFromUser(self, block):
        if self.blockVerification(block):
            if self.addBlockToChain(block):
                self.sendBlock(block)
                return True
        else:
            return False
            
    def addNewBlockFromNet(self, block):
        if self.blockVerification(block):
            self.addBlockToChain(block)

    def sendTransact(self, Transact):
        self.CNetwork.sendMessageAll(Transact, consts.typeNetQuery.get('transaction'))
        return True

    def transactionVerification(self, Transaction):
        type = Transaction['type']

        jsonTransact = copy.deepcopy(Transaction)
        signature = jsonTransact.pop('signature')
        jsonTransact.pop('idBlock', None)
        jsonTransact.pop('hash', None)
        jsonTransact.pop('idTransaction',None)

        string = json.dumps(jsonTransact, sort_keys=True)

        pubKey = CAccountingSystem.CAccountingSystem.stringToPublicKey(Transaction['publicKey'])

        if not (CAccountingSystem.CAccountingSystem.checkSignature(pubKey, string, signature)):
            return False

        if type == 0:
            if not self.newTransaction_registration(Transaction):
                return False
        if type == 1:
            if not self.newTransaction_promotion(Transaction):
                return False
        if type == 2:
            if not self.newTransaction_reduction(Transaction):
                return False
        if type == 3:
            if not self.newTransaction_confirmPromotionOrReduction(Transaction):
                return False
        if type == 4:
            if not self.newTransaction_confirmChangeEvent(Transaction):
                return False
        if type == 5:
            if not self.newTransaction_CreateEvent(Transaction):
                return False
        if type == 6:
            if not self.newTransaction_ChangeEvent(Transaction):
                return False
        return True

    def ParseNewTrasnactionFromBlock(self, InputTransaction, CreateTime):
        type = InputTransaction['type']

        Transaction = copy.deepcopy(InputTransaction)


        if type == 0:
            self.addNewTransaction_registration(Transaction)
        if type == 1:
            self.addNewTransaction_promotion(Transaction, CreateTime)
        if type == 2:
            self.addNewTransaction_reduction(Transaction, CreateTime)
        if type == 3:
            self.addNewTransaction_confirmPromotionOrReduction(Transaction, CreateTime)
        if type == 4:
            self.addNewTransaction_confirmChangeEvent(Transaction, CreateTime)
        if type == 5:
            self.addNewTransaction_CreateEvent(Transaction, CreateTime)
        if type == 6:
            self.addNewTransaction_ChangeEvent(Transaction, CreateTime)
        if type == 10:
            self.addNewTransaction_checkSingatureTransact(Transaction)

    def blockVerification(self, block):
            LastBlockId = self.dataBaseAdapt.getLastBlock()[consts.BlockColumns.get('idBlock')]
            LastBlockHash = self.dataBaseAdapt.getLastBlock()[consts.BlockColumns.get('hash')]

            if not (block['idBlock'] == LastBlockId + 1):
                return False
            if not (str(block['previousBlockHash']) == str(LastBlockHash)):
                return False
            TransactInBlockList = block['transactionList']
            if len(TransactInBlockList) <= 1:
                return False
            if not (self.checkAutorTransact(TransactInBlockList[len(TransactInBlockList)-1])):
                return False
            complexity = self.determineComplexityHash(TransactInBlockList[len(TransactInBlockList)-1]['address'])
            if complexity != block['complexity']:
                return False
            if complexity == block['hash'][:-len(complexity)]:
                return False


            string = ""
            string += str(block['idBlock'])
            string += str(block['previousBlockHash'])
            string += str(block['time'])
            string += complexity
            string = string

            TransactInBlockList = block['transactionList']

            for element in TransactInBlockList:
                if type(element['data']) == str:
                    element['data'] = json.loads(element['data'])

            Transact = copy.deepcopy(TransactInBlockList)
            for element in Transact:
                element.pop('idTransaction', None)
                element.pop('idBlock', None)
                element.pop('hash', None)
                string += json.dumps(element, sort_keys=True)

            l = hashlib.sha256((string + str(block['nonce'])).encode()).hexdigest()
            if hashlib.sha256((string + str(block['nonce'])).encode()).hexdigest() != block['hash']:
                return False

            for element in TransactInBlockList:
                if (self.transactionVerification(element)):
                    pass
                else:
                    return False

            return True

    def getLastblock(self):
        return(self.dataBaseAdapt.getLastBlock())

    def resetBlock(self, NumberOfMaxBlock):
        length = self.dataBaseAdapt.getLastBlock()[consts.BlockColumns.get('idBlock')]
        for i in range(length,-1,-1):
            if i >= NumberOfMaxBlock:
                block = self.dataBaseAdapt.getLastBlock()
                CreateTime = block[consts.BlockColumns.get('timestamp')]
                TransactList = self.dataBaseAdapt.getTransactByIdBlock(block[consts.BlockColumns.get('idBlock')])
                self.dataBaseAdapt.delBlock(block[consts.BlockColumns.get('idBlock')])
                for element in TransactList:
                    self.deleteTransact(element, CreateTime)

    def deleteTransact(self, Transact, CreateTime):
        type =  Transact[consts.transaction.get('type')]

        Transaction = {
        'idTransaction': Transact[0],
        'type': Transact[2],
        'data': Transact[3],
        'publicKey': Transact[4],
        'hash': Transact[5],
        'signature': Transact[6],
        'address': Transact[7],
        'idBlock': Transact[1]
        }

        Transaction['data'] = json.loads(Transaction['data'])

        if type == 0:
            self.delTransaction_registration(Transaction)
        if type == 1:
            self.delTransaction_promotion(Transaction, CreateTime)
        if type == 2:
            self.delTransaction_reduction(Transaction, CreateTime)
        if type == 3:
            self.delTransaction_confirmPromotionOrReduction(Transaction, CreateTime)
        if type == 4:
            self.delTransaction_confirmChangeEvent(Transaction, CreateTime)
        if type == 5:
            self.delTransaction_CreateEvent(Transaction, CreateTime)
        if type == 6:
            self.delTransaction_ChangeEvent(Transaction, CreateTime)
        if type == 10:
            self.delTransactionFromTransactionTable(Transaction)


    def addNewTransaction_registration(self, Transaction):
        address = Transaction['address']
        name = Transaction['data']['name']
        organization = Transaction['data']['organization']
        brirthday = Transaction['data']['birthday']
        isExpert = 0
        publicKey = Transaction['publicKey']
        self.dataBaseAdapt.addUser(address, name, brirthday, isExpert, publicKey, organization)
        self.addTransactionToTransactionTable(Transaction)
        return True

    def delTransaction_registration(self, Transaction):
        address = Transaction['address']
        self.dataBaseAdapt.delUser(address)
        self.delTransactionFromTransactionTable(Transaction)

    def addNewTransaction_promotion(self, Transaction, CreateTime):
        address = Transaction['address']
        self.dataBaseAdapt.addRequestRise(address, CreateTime)
        self.addTransactionToTransactionTable(Transaction)

    def delTransaction_promotion(self, Transaction, CreateTime):
        address = Transaction['address']
        self.dataBaseAdapt.delRequestRise(address, CreateTime)
        self.delTransactionFromTransactionTable(Transaction)

    def addNewTransaction_reduction(self, Transaction, CreateTime):
        addressFrom = Transaction['address']
        addressTo = Transaction['data']['address']
        self.dataBaseAdapt.addRequestDemot(addressFrom, addressTo, CreateTime)
        self.addTransactionToTransactionTable(Transaction)

    def delTransaction_reduction(self, Transaction, CreateTime):
        addressFrom = Transaction['address']
        addressTo = Transaction['data']['address']
        self.dataBaseAdapt.delRequestDemot(addressFrom, addressTo, CreateTime)
        self.delTransactionFromTransactionTable(Transaction)

    def addNewTransaction_confirmPromotionOrReduction(self, Transaction, CreateTime):
        address = Transaction['address']
        idRequest = Transaction['data']['idRequest']
        request = self.dataBaseAdapt.getRequestById(idRequest)
        if (CreateTime - request[consts.requestColumns.get('date')])/3600 <= 24:
            self.dataBaseAdapt.addAccept(idRequest, address)
        self.addTransactionToTransactionTable(Transaction)

        request = self.dataBaseAdapt.getRequestById(idRequest)
        if request[consts.requestColumns.get('quantityAccepted')] == 3:
            if request[consts.requestColumns.get('typeRequest')] == 0:
                self.dataBaseAdapt.setExpert(Transaction['data']['address'])
            if request[consts.requestColumns.get('typeRequest')] == 1:
                self.dataBaseAdapt.setStudent(Transaction['data']['address'])

    def delTransaction_confirmPromotionOrReduction(self, Transaction, CreateTime):
        address = Transaction['address']
        idRequest = Transaction['data']['idRequest']
        request = self.dataBaseAdapt.getRequestById(idRequest)
        if (CreateTime - request[consts.requestColumns.get('date')]) / 3600 <= 24:
            self.dataBaseAdapt.delAccept(idRequest, address)
        self.delTransactionFromTransactionTable(Transaction)

        request = self.dataBaseAdapt.getRequestById(idRequest)
        if request[consts.requestColumns.get('quantityAccepted')] < 3:
            if request[consts.requestColumns.get('typeRequest')] == 1:
                print(self.dataBaseAdapt.setExpert(address))
            if request[consts.requestColumns.get('typeRequest')] == 0:
                self.dataBaseAdapt.setStudent(address)

    def addNewTransaction_confirmChangeEvent(self, Transaction, CreateTime):
        addressExpert = Transaction['address']
        updateIndex = Transaction['data']['updateIndex']
        idEvent = Transaction['data']['idEvent']

        changeEvent = self.dataBaseAdapt.getEvent(idEvent)
        if (CreateTime - changeEvent[consts.eventsUpdateColumns.get('timestamp')])/3600 <=24:
            self.dataBaseAdapt.addAcceptUpdateEvent(idEvent, updateIndex, addressExpert)
        self.addTransactionToTransactionTable(Transaction)

        listOfAllChangeEvent = self.dataBaseAdapt.getEventUpdateListAtEvent(idEvent)
        if listOfAllChangeEvent != None:
            for element in listOfAllChangeEvent:
                countOfExpert = len(self.dataBaseAdapt.getEventUpdateExpertList(element['idEvent']))
                if element[consts.eventsUpdateColumns.get('numOfExperts')] == countOfExpert:
                    self.eventChange(element)


    def eventChange(self, EventChangeTransact):
        self.dataBaseAdapt.changeEvent(EventChangeTransact['data']['idEvent'], EventChangeTransact['data']['name'],
                                       EventChangeTransact['data']['info'], EventChangeTransact['data']['date'],
                                       EventChangeTransact['data']['competence'], EventChangeTransact['data']['rating'],
                                       len(EventChangeTransact['data']['experts']), EventChangeTransact['data']['experts'],
                                       EventChangeTransact['data']['users'])

    def delTransaction_confirmChangeEvent(self, Transaction, CreateTime):
        addressExpert = Transaction['address']
        updateIndex = Transaction['data']['updateIndex']
        idEvent = Transaction['data']['idEvent']

        changeEvent = self.dataBaseAdapt.getEvent(idEvent)
        if (CreateTime - changeEvent[consts.eventsUpdateColumns.get('timestamp')])/3600 <=24:
            self.dataBaseAdapt.delAcceptUpdateEvent(idEvent, updateIndex, addressExpert)
        self.delTransactionFromTransactionTable(Transaction)

    def addNewTransaction_CreateEvent(self, Transaction, CreateTime):
        name = Transaction['data']['name']
        date = Transaction['data']['date']
        competence = Transaction['data']['competence']
        data = Transaction['data']['info']
        UserList = Transaction['data']['users']
        ExpertList = Transaction['data']['experts']
        creator = Transaction['address']
        timestamp = CreateTime
        rating = 0
        self.dataBaseAdapt.addEvent(creator, name, date, data, competence, rating, len(ExpertList), ExpertList,
                                    UserList,timestamp)
        self.addTransactionToTransactionTable(Transaction)

    def delTransaction_CreateEvent(self, Transaction, CreateTime):
        name = Transaction['data']['name']
        date = Transaction['data']['date']
        competence = Transaction['data']['competence']
        rating = 0
        data = Transaction['data']['info']
        UserList = Transaction['data']['users']
        ExpertList = Transaction['data']['experts']
        creator = Transaction['address']
        timestamp = CreateTime

        self.dataBaseAdapt.delEvent(creator, name, date, data, competence, rating, len(ExpertList), ExpertList,
                                    UserList,timestamp)
        self.delTransactionFromTransactionTable(Transaction)

    def addNewTransaction_ChangeEvent(self, Transaction, CreateTime):
        idEvent = Transaction['data']['idEvent']
        name = Transaction['data']['name']
        date = Transaction['data']['date']
        competence = Transaction['data']['competence']
        data = Transaction['data']['info']
        UserList = Transaction['data']['users']
        ExpertList = Transaction['data']['experts']
        lenExpertList = None
        if ExpertList != None:
            lenExpertList = len(ExpertList)
        self.dataBaseAdapt.addEventUpdate(idEvent, name, data, date, competence, lenExpertList, ExpertList, UserList,
                                          CreateTime)
        self.addTransactionToTransactionTable(Transaction)

    def delTransaction_ChangeEvent(self, Transaction, CreateTime):
        idEvent = Transaction['data']['idEvent']
        name = Transaction['data']['name']
        date = Transaction['data']['date']
        competence = Transaction['data']['competence']
        data = Transaction['data']['info']
        UserList = Transaction['data']['users']
        ExpertList = Transaction['data']['experts']
        lenExpertList = None
        if ExpertList != None:
            lenExpertList = len(ExpertList)
        self.dataBaseAdapt.delEventUpdate(idEvent, name, data, date, competence, lenExpertList, ExpertList, UserList,
                                          CreateTime)
        self.delTransactionFromTransactionTable(Transaction)

    def addNewTransaction_checkSingatureTransact(self, Transaction):
        self.addTransactionToTransactionTable(Transaction)

    def delTransaction_checkSingatureTransact(self, Transaction):
        self.delTransactionFromTransactionTable(Transaction)

    def newTransaction_registration(self, Transaction):
        L = len(str(Transaction['address']))
        if not (len(str(Transaction['address']))):
            return False
        if not (self.dataBaseAdapt.getUser(Transaction['address']) == None):
            return False
        return (True)

    def addTransactionToTransactionTable(self, Transaction):
        self.dataBaseAdapt.addTransaction(Transaction['address'], Transaction['type'], json.dumps(Transaction['data']),
                                          Transaction['publicKey'], Transaction['signature'], Transaction['idBlock'])

    def delTransactionFromTransactionTable(self, Transaction):
        self.dataBaseAdapt.delTransaction(Transaction['address'], Transaction['type'], json.dumps(Transaction['data']),
                                          Transaction['publicKey'], Transaction['signature'], Transaction['idBlock'])

    def newTransaction_promotion(self, Transaction):
        if not (len(str(Transaction['address']))):
            return False
        if not (self.dataBaseAdapt.getIsExpert(Transaction['address']) == 0):
            return False
        return (True)

    def newTransaction_reduction(self, Transaction):
        if not (len(str(Transaction['address']))):
            return False
        if not (self.dataBaseAdapt.getIsExpert(Transaction['address']) == 1):
            return False
        if not (len(str(Transaction['data']['address']))):
            return False
        if not (self.dataBaseAdapt.getIsExpert(Transaction['data']['address']) == 1):
            return False

        return (True)

    def newTransaction_confirmPromotionOrReduction(self, Transaction):
        if not (len(str(Transaction['address']))):
            return False
        if not (self.dataBaseAdapt.getIsExpert(Transaction['address']) == 1):
            return False
        if (self.dataBaseAdapt.getRequestById(Transaction['data']['idRequest']) == None):
            return False


        return (True)

    def newTransaction_confirmChangeEvent(self, Transaction):
        if not (len(str(Transaction['address']))):
            return False
        if not (self.dataBaseAdapt.getIsExpert(Transaction['address']) == 1):
            return False
        if (self.dataBaseAdapt.getEventUpdate(Transaction['data']['idEvent'],Transaction['data']['updateIndex']) == None):
            return False
        return (True)

    def newTransaction_CreateEvent(self, Transaction):
        if not (len(str(Transaction['address']))):
            return False
        if not (self.dataBaseAdapt.getIsExpert(Transaction['address']) == 1):
            return False
        if (len(Transaction['data']['experts']) == 0):
            return False
        expertsList = Transaction['data']['experts']
        usersList = Transaction['data']['users']

        for element in expertsList:
            if element in usersList:
                return False
            if not (self.dataBaseAdapt.getIsExpert(element[consts.usersColumns['addres']]) == 1):
                return False

        return (True)

    def newTransaction_ChangeEvent(self, Transaction):
        if not (len(str(Transaction['address']))):
            return False
        if not (self.dataBaseAdapt.getIsExpert(Transaction['address']) == 1):
            return False
        if (self.dataBaseAdapt.getEvent(Transaction['data']['idEvent']) == None):
            return False
        if (len(Transaction['data']['experts']) == 0):
            return False

        expertsList = Transaction['data']['experts']
        usersList = Transaction['data']['users']

        for element in expertsList:
            if element in usersList:
                return False
            if not (self.dataBaseAdapt.getIsExpert(element[consts.usersColumns['addres']]) == 1):
                return False
        return(True)

    def addTransactToUncTransact(self, Transaction):
        UncTransactList = self.dataBaseAdapt.getUncTransactionList()
        if UncTransactList != None:
            for element in UncTransactList:
                if (Transaction['address'] == element[consts.UncTransaction.get('address')]) & \
                   (Transaction['type'] == element[consts.UncTransaction.get('type')]) & \
                   (json.dumps(Transaction['data']) == element[consts.UncTransaction.get('data')]) & \
                   (Transaction['publicKey'] == element[consts.UncTransaction.get('publicKey')]) & \
                   (Transaction['signature'] == element[consts.UncTransaction.get('signature')]):
                    return False
        self.dataBaseAdapt.addUncTransaction(Transaction['address'], Transaction['type'], json.dumps(Transaction['data']),
                                             Transaction['publicKey'], Transaction['signature'])
        return True

    def MineBlock(self):
        Address = CAccountingSystem.CAccountingSystem.publicKeyToAddress(self.PrivateKey)
        Complexity = self.determineComplexityHash(Address)
        LastBlockId = self.dataBaseAdapt.getLastBlock()[consts.BlockColumns.get('idBlock')]
        LastBlockHash = self.dataBaseAdapt.getLastBlock()[consts.BlockColumns.get('hash')]
        createTime = time.time()

        if (Complexity) == False:
            return "Нет прав"
        countOfUncTransact = self.dataBaseAdapt.getCountOfUncTransaction()
        if (countOfUncTransact == None):
            return "Какая-то ошибка"
        if (countOfUncTransact == 0):
            return "Нету транзакций"
        UncTransact = self.dataBaseAdapt.getUncTransactionList()

        if len(UncTransact) < 10:
            time.sleep(2)  #todo 10*60 - len(UncTransact)

        print('try to Mine')

        UncTransact = self.dataBaseAdapt.getUncTransactionList()
        if len(UncTransact) >= 10:
            UncTransact = UncTransact[:8]

        UncTransact = self.fromTupleToDict(UncTransact)
        UncTransact.append(self.createAutorTransact())

        for element in UncTransact:
            element['idBlock'] = LastBlockId + 1
            if type(element['data']) == str:
                element['data'] = json.loads(element['data'])


        string = ""
        string += str(LastBlockId + 1)
        string += str(LastBlockHash)
        string += str(createTime)
        string += Complexity

        Transact = copy.deepcopy(UncTransact)
        for element in Transact:
            element.pop('idTransaction', None)
            element.pop('idBlock', None)
            element.pop('hash', None)
            string += json.dumps(element, sort_keys=True)

        nonce = 0
        while hashlib.sha256((string + str(nonce)).encode()).hexdigest()[-len(Complexity):] != Complexity:
            nonce += 1
        hashBlock = hashlib.sha256((string + str(nonce)).encode()).hexdigest()
        block = self.createBlock(UncTransact, nonce, LastBlockId + 1, hashBlock, LastBlockHash, createTime, Complexity)
        if True:
            self.addNewBlockFromUser(block)

            return True
        return False

    def startMine(self):
        while True:
            while self._MineStat:
                self.MineBlock()

    def fromTupleToDict(self, UncTransact):
        DictList = []
        for element in UncTransact:
            Dict = {
                'idTransaction': element[0],
                'type': element[1],
                'data': element[2],
                'publicKey': element[3],
                'hash': element[4],
                'signature': element[5],
                'address': element[6],
            }
            DictList.append(Dict)
        return (DictList)

    def createBlock(self, UncTransact, nonce, currentBlockId, hashBlock, LastBlockHash, createTime, Complexity):
        block = {}
        block['nonce'] = nonce
        block['idBlock'] = currentBlockId
        block['hash'] = hashBlock
        block['previousBlockHash'] = LastBlockHash
        block['time'] = createTime
        block['complexity'] = Complexity
        block['transactionList'] = UncTransact
        return block

    def addBlockToChain(self, blockOrig):

        TransactInBlockList = blockOrig['transactionList']
        for element in TransactInBlockList:
            if type(element['data']) == str:
                element['data'] = json.loads(element['data'])

        UncTransactList = self.dataBaseAdapt.getUncTransactionList()
        TransactInBlockCheckList = copy.deepcopy(TransactInBlockList)
        for element in TransactInBlockCheckList:
            element.pop('idBlock', None)
            element.pop('idTransaction', None)

        listOfIdUncTransact = []
        UncTransactList = self.fromTupleToDict(UncTransactList)
        for element in UncTransactList:
            listOfIdUncTransact.append(element['idTransaction'])
            element.pop('idTransaction', None)
            element['data'] = json.loads(element['data'])

        i = 0
        for element in TransactInBlockCheckList:
            for element2 in UncTransactList:
                if (element.get('signature') == element2.get('signature')):
                    self.dataBaseAdapt.deleteUncTransaction(listOfIdUncTransact[i])
            i += 1

        CreateTime = blockOrig['time']
        for element in blockOrig['transactionList']:
            element['idBlock'] = blockOrig['idBlock']
            self.ParseNewTrasnactionFromBlock(element, CreateTime)

        block = copy.deepcopy(blockOrig)
        block.pop('transactionList')
        self.dataBaseAdapt.addBlock(block['hash'],block['time'],47,block['complexity'],block['nonce'])
        self._ReloadFunction()

    def sendBlock(self, block):
        self.CNetwork.sendMessageAll(block,consts.typeNetQuery.get('block'))

    def createAutorTransact(self):
        Address = CAccountingSystem.CAccountingSystem.publicKeyToAddress(self.PrivateKey)

        TransactionDict = {}
        TransactionDict['address'] = Address
        TransactionDict['type'] = 10
        TransactionDict['data'] = {'Hello': "ow, Hello you to"}
        PubKey = CAccountingSystem.CAccountingSystem.privateKeyToPublic(self.PrivateKey)
        TransactionDict['publicKey'] = CAccountingSystem.CAccountingSystem.publicKeyToString(PubKey)

        string = json.dumps(TransactionDict, sort_keys=True)
        TransactionDict['publicKey'] = TransactionDict['publicKey']
        privKey = self.PrivateKey
        TransactionDict['signature'] = CAccountingSystem.CAccountingSystem.createSingature(privKey, string)

        return (TransactionDict)

    def checkAutorTransact(self, OriginalTransact):
        Transact = copy.deepcopy(OriginalTransact)
        if Transact['type'] != 10:
            return False
        Address = Transact['address']
        if (self.dataBaseAdapt.getUser(Address) == None):
            return False
        pubKey = CAccountingSystem.CAccountingSystem.stringToPublicKey(Transact['publicKey'])
        if CAccountingSystem.CAccountingSystem.publicKeyToAddress(pubKey) != Address:
            return False
        signature = Transact['signature']
        Transact.pop('signature', None)
        Transact.pop('idBlock', None)
        Transact['publicKey'] = Transact['publicKey']
        if type(Transact['data']) == str:
            Transact['data'] = json.loads(Transact['data'])

        string = json.dumps(Transact, sort_keys=True)
        if not (CAccountingSystem.CAccountingSystem.checkSignature(pubKey, string, signature)):
            return False

        return True

    def determineComplexityHash(self, Address):
        complexity = "000000"
        if (self.dataBaseAdapt.getUser(Address) == None):
            return False
        if (self.dataBaseAdapt.getIsExpert(Address) == 1):
            complexity = Complexity["expert"]
        if (self.dataBaseAdapt.getIsExpert(Address) == 0):
            complexity = Complexity["user"]
        return (complexity)

    def getLengthChain(self):
        block = self.dataBaseAdapt.getLastBlock()
        length = block[consts.BlockColumns.get('idBlock')]
        return length



    def compareBlockChainWithNet(self, hashChain):
        MyHashChainTuple = self.dataBaseAdapt.getHashChain()
        MyHashChain = []
        for element in MyHashChainTuple:
            MyHashChain.append(list(element))

        differentHashChain = []
        for i in range(len(MyHashChain)):
            if hashChain[i] == MyHashChain[i]:
                pass
            if hashChain[i] != MyHashChain[i]:
                differentHashChain.append(hashChain[i])
        if len(MyHashChain) < len(hashChain):
            i = len(MyHashChain) + 1
            while i <= len(hashChain):
                differentHashChain.append(hashChain[i-1])
                i += 1

        if len(differentHashChain):
            return differentHashChain
        else:
            return False

    def getBlockListByHashList(self, hashChain):
        blockList = []
        for element in hashChain:
            block = self.dataBaseAdapt.getBlockByHash(element[0])
            transactTupleList = self.dataBaseAdapt.getTransactByIdBlock(block[consts.BlockColumns.get('idBlock')])
            transactDictList = []
            for element in transactTupleList:
                transaction = {
                    'idTransaction': element[0],
                    'type': element[2],
                    'data': element[3],
                    'publicKey': element[4],
                    'hash': element[5],
                    'signature': element[6],
                    'address': element[7],
                    'idBlock': element[1]
                }
                transactDictList.append(transaction)

            blockList.append(self.createBlock(transactDictList, block[consts.BlockColumns.get('nonce')],
                             block[consts.BlockColumns.get('idBlock')], block[consts.BlockColumns.get('hash')],
                             block[consts.BlockColumns.get('PrevBlockHash')],
                             block[consts.BlockColumns.get('timestamp')], block[consts.BlockColumns.get('complexity')]))

        return blockList


    def getBlockChainHashChain(self):
        chainOfHash = self.dataBaseAdapt.getHashChain()
        return chainOfHash







