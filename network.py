# -*- coding: utf-8 -*-
import socket
import json
import sqlite3
import consts
from collections import OrderedDict
import Block_chain
import time
#import Block_chain
#import receivedMessagesParser

class network:
    def __init__(self,blockchain):
        '''
        Initialization class  works with network.
        :param blockchain: class Blockchain
        '''
        self.lastIndex = 0
        self.processingStep = 0
        self.blockchain = blockchain

    def sendMessage(self, data, type, addres):
        '''
        This method send message to user  by  network address
        :param self:
        :param data: data
        :param type: messages's type( types are identified consts.typeNetQuery)
        :param addres: network address
        :return:
        '''
        #try:
        dict = {
            'type' : type,
            'data' : data
        }

        bytesData = json.dumps(dict)
        sock = socket.socket()
        try:
            sock.connect((addres, 9090))
            sock.send(bytesData.encode())
            sock.close()
        except:
            sock.close()
            pass
       # except:
         #   return None

    def sendMessageAll(self,data,type):
        '''
        This method send message to all addreses in db
        Args:
        :param self:
        :param data: data
        :param type: messages's type( types are identified consts.typeNetQuery)
        :return:
        '''
        #try:
        addreses = self.getNetwork()
        for addr in addreses:
            self.sendMessage(data,type,addr[0])
        #except:
        #    return None


    def receiveMessage(self):
        '''
        This method reseive messages(from all users in network) port : 9090
        :param self:
        :return:
        '''
        while True:
            sock = socket.socket()
            sock.bind(('', 9090))
            sock.listen(100)
            while True:
                conn, addr = sock.accept()
                self.addAddres(addr[0])
                #try:
                data = conn.recv(16388)
                print(data)
                dict = json.loads(data)
                sender = {'sender' : addr[0]}
                dict.update(sender)
                self.parserAndRunQuery(dict)
                try:
                    pass
                except Exception as e:
                    dict = {
                        'type': consts.typeNetQuery.get('error'),
                        'data': None
                    }
                    bytesData = json.dumps(dict)
                    sock.connect((addr[0], 9090))
                    sock.send(bytesData)
                finally:
                    conn.close()


    def addAddres(self, addres):
        '''
        This method adding address in db.addres
        :param self:
        :param address: user's network addresses
        :return:
        '''
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO addres (addres) VALUES ('%s')"%(addres))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            return None

    def getNetwork(self):
        '''
        This method return all addresses in network
        :param self:
        :return: rows from db.address
        '''
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT addres.addres FROM addres")
            rows = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            return rows
        except:
            return None


    def parserAndRunQuery(self, dictionary):
        '''
        This method parse received messages, analyze and work with messages(Type in message - appropriate handler)
        :param self:
        :param dictionary: is message(type dictionary)
        :return:
        '''
        type = dictionary.get('type')
        data = dictionary.get('data')
        addres = dictionary.get('sender')
        if (type == consts.typeNetQuery.get('transaction')):
            self.blockchain.addNewTransactFromNet(data)
            return
        if (type == consts.typeNetQuery.get('block')):
            self.blockchain.addNewBlockFromNet(data)
            return
        if (type == consts.typeNetQuery.get('length')):
            # Не пришло данных значит это запрос
            if (data == None):
                countBlock = self.blockchain.getLengthChain()
                self.sendMessage(countBlock, consts.typeNetQuery.get('length'), addres)
                return
            else:
                countBlock = data
                mylen = self.blockchain.getLengthChain()
                if (countBlock == mylen):
                    self.processingStep = 0
                    return False
                if (countBlock < mylen):
                    self.processingStep = 0
                    return False
                if (countBlock > mylen):
                    self.processingStep = 1
                    self.sendMessage(None, consts.typeNetQuery.get('fullChain'), addres)

        if (type == consts.typeNetQuery.get('fullChain')):
            if (data == None):
                hashChain = self.blockchain.getBlockChainHashChain()
                self.sendMessage(hashChain, consts.typeNetQuery.get('fullChain'), addres)
                return
            else:
                HashList = self.blockchain.compareBlockChainWithNet(data)
                if HashList == False:
                    self.processingStep = 0
                    return False
                else:
                    self.processingStep = 2
                    self.sendMessage(HashList, consts.typeNetQuery.get('SendHashChain'), addres)
                return
        if (type == consts.typeNetQuery.get('SendHashChain')):
            if (data == None):
                return False
            else:
                hashChain = data
                BlockList = self.blockchain.getBlockListByHashList(hashChain)
                self.sendMessage(BlockList, consts.typeNetQuery.get('SendBlockList'), addres)

        if (type == consts.typeNetQuery.get('SendBlockList')):
            if (data == None):
                return False
            else:
                BlockList = data

                self.processingStep = 3
                length = self.blockchain.getLengthChain()

                if length <= BlockList[0]['idBlock']:
                    self.blockchain.resetBlock(BlockList[0]['idBlock'])

                for element in BlockList:
                    for trans in element['transactionList']:
                        trans.pop('idBlock', None)
                        trans.pop('idTransaction', None)
                        trans.pop('hash', None)


                    self.blockchain.addNewBlockFromNet(element)
                self.processingStep = 0

        if (type == consts.typeNetQuery.get('eqChain')):
            #цепочка одинаковая у всех - делать ничего не надо
            return
        if (type == consts.typeNetQuery.get('notEqChain')):
            #Здесь надо как-то менять свою цепочку
            return
        if (type == consts.typeNetQuery.get('addUser')):
            # Не пришло данных значит это запрос на получение сети(добавление в сеть)
            if (data == None):
                self.sendMessage(self.getNetwork(), consts.typeNetQuery.get('addUser'), addres)
            else:
                for row in data:
                    self.addAddres(row[0])


    def lenCheckerNeighbourhood(self):
        while True:
            addreses = self.getNetwork()
            data = None
            type = consts.typeNetQuery.get('length')
            for addr in addreses:
                try:
                    if self.processingStep == 0:
                        self.sendMessage(data, type, addr[0])
                        self.processingStep == 1
                        time.sleep(20)
                except:
                    pass
        return False

