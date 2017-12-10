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

'''
1- новая транзакций
#2- новый блок
#3- опросить соседей на длину их цепочки
#4- запросить всю цепочку у соседей
#5- (как-то свериться с цепочкой соседей и, возможно, запросить только те блоки, с которых началось различие)
#6- все запросы касательно добавления нового члена в сеть(новый айпи, дать список существующих айпи, запросить список существующих айпи)
Это все есть в consts.typeNetQuery
'''
class network:
    def __init__(self,blockchain):
       # self.receiveMessage()
        self.blockchain = blockchain
        #self.sendMessage('Hello','addUser','127.0.0.1')

    def sendMessage(self, data, type, addres):
        #try:
            dict = {
                'type' : type,
                'data' : data
            }
            print('send:')
            print(addres)
            print(dict)

            bytesData = json.dumps(dict)
            sock = socket.socket()
            sock.connect((addres, 9090))
            sock.send(bytesData.encode())
            sock.close()

       # except:
         #   return None

    def sendMessageAll(self,data,type):
        #try:
            print('send:')
            print(data)
            addreses = self.getNetwork()
            for addr in addreses:
                self.sendMessage(data,type,addr[0])
        #except:
        #    return None


    def receiveMessage(self):
        while True:
            sock = socket.socket()
            sock.bind(('', 9090))
            sock.listen(100)
            while True:
                conn, addr = sock.accept()
                self.addAddres(addr[0])
                print("New connection from " + addr[0])
                #try:
                data = conn.recv(16388)

                dict = json.loads(data)
                sender = {'sender' : addr[0]}
                dict.update(sender)
                print('prinyal:')
                print(dict)
                self.parserAndRunQuery(dict)
                try:
                    pass
                except Exception as e:
                    print(e)
                    dict = {
                        'type': consts.typeNetQuery.get('error'),
                        'data': None
                    }
                    bytesData = json.dumps(dict)
                    sock.connect((addr[0], 9090))
                    sock.send(bytesData)
                finally:
                    conn.close()

    #Кинул сюда запрос,чтобы каждый раз адаптер сюда не засылать
    def addAddres(self, addres):
        try:
            print(addres)
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO addres (addres) VALUES ('%s')"%(addres))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            return None

    def getNetwork(self):
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


    def parserAndRunQuery(self,dictioary):
        type = dictioary.get('type')
        data = dictioary.get('data')
        addres = dictioary.get('sender')
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
                    pass
                if (countBlock < mylen):
                    pass
                if (countBlock > mylen):
                    self.sendMessage(None, consts.typeNetQuery.get('fullChain'), addres)

        if (type == consts.typeNetQuery.get('fullChain')):
            if (data == None):
                hashChain = self.blockchain.getBlockChainHashChain()
                self.sendMessage(hashChain, consts.typeNetQuery.get('fullChain'), addres)
                return
            else:
                HashList = self.blockchain.compareBlockChainWithNet(data)
                if HashList == False:
                    pass
                else:
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
                for element in BlockList:
                    self.blockchain.addNewBlockFromNet(element)

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






#receiveMessage()
#sendMessage('2312312314215',1,'10.121.6.179')
network('dsfsdf')