#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cmd
import os
import json
import rsa

import Block_chain
import CAccountingSystem
import network
import dataBaseAdapter

def getPrivateKeyFromFile(fname):
    try:
        fname = os.path.abspath(fname)
        f = open(fname, 'r')
        l = f.readlines()

        n = int(l[0][:-1])
        e = int(l[1][:-1])
        d = int(l[2][:-1])
        p = int(l[3][:-1])
        q = int(l[4][:-1])
        PrivateKey = rsa.PrivateKey(n,e,d,p,q)
        return (PrivateKey)
    except Exception as e:
        print("Внимание", "Неправильный путь до ключа")
        return False

class Cli(cmd.Cmd):
    accountSystemClass = None
    dataBaseAdapter = None
    CblockChain = None
    Cnetwork = None
    isAuth = False

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.dataBaseAdapt = dataBaseAdapter.dataBaseAdapter()
        self.accountSystemClass = CAccountingSystem.CAccountingSystem(self.dataBaseAdapt)
        self.CblockChain = Block_chain.Blockchain()
        self.Cnetwork = network.network(self.CblockChain)
        self.CblockChain.InitAddNetWork(self.Cnetwork)
        self.prompt = "(not auth)> "
        self.intro  = "Добро пожаловать\nДля справки наберите 'help'"
        self.doc_header ="Доступные команды (для справки по конкретной команде наберите 'help _команда_')"

    def do_hello(self, args):
        """hello - выводит 'hello world' на экран"""
        print ('hello world')

    def default(self, line):
        print ('Несуществующая команда')

    def do_addUser(self, args):
        #print('Введите свое имя')
        name = input('Введите свое имя')
        #print (name)
        #print (args)

    def do_login(self, args):
        pathToPrivateKey = input('Please enter path to file with your private key:\n ')
        privateKey = getPrivateKeyFromFile(pathToPrivateKey)
        if not (privateKey):
            print('Error. Not found your private key or incorrect')
            return False

        if (self.accountSystemClass.authorization(privateKey)):
            self.CblockChain.setPrivateKey(privateKey)
            self.prompt = "> "
            self.isAuth = True
        else:
            print("Attention", "User not exist")

    def do_logout(self,args):
        self.accountSystemClass.logout()
        print("Attention", "You are logout ")
        self.prompt = "(not auth)> "
        self.isAuth = False

    def generatePrivateKey(self):
        privateKey = self.accountSystemClass.generateKey()
        s = 0
        stat = True

        while stat:
            if not os.path.exists('keys/PrivateKey_' + str(s)):
                    f = open('keys/PrivateKey_' + str(s),'w')
                    stat = False
            else:
                    s = s+1
        f.write(str(privateKey.n) + '\n')
        f.write(str(privateKey.e) + '\n')
        f.write(str(privateKey.d) + '\n')
        f.write(str(privateKey.p) + '\n')
        f.write(str(privateKey.q) + '\n')
        print(self, "Attention", "The key is created in the program folder. Please save it.")
        absolutePathToFile = os.path.abspath('keys/PrivateKey_' + str(s))
        return absolutePathToFile

    def do_createNewUser(self,argv):
        Transaction = {}
        datadict = {}
        datadict['organization'] = input('Input your orhanization')
        datadict['name'] = input('Input your full name ')
        datadict['birthday'] = input('Input your birthday')

        Transaction['data'] = datadict
        Transaction['type'] = 0
        path = self.generatePrivateKey()
        print('Your file is ', path)
        privateKey = self.getPrivateKeyFromFile(path)
        Transaction['address'] = self.accountSystemClass.publicKeyToAddress(privateKey)
        Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(privateKey)
        string = json.dumps(Transaction, sort_keys = True)
        signature = self.accountSystemClass.createSingature(privateKey, string)
        Transaction['signature'] = signature
        if not (self.CblockChain.addNewTransactFromUser(Transaction)):
            print( "Error", "Something went wrong")
            return False
        print("Attention", "You sent a registration request. "
                                            "Please wait while one of the registered users "
                                            "system will not confirm your registration")

    def getPrivateKeyFromFile(self, fname):
        try:
            f = open(fname, 'r')
            l = f.readlines()

            n = int(l[0][:-1])
            e = int(l[1][:-1])
            d = int(l[2][:-1])
            p = int(l[3][:-1])
            q = int(l[4][:-1])
            PrivateKey = rsa.PrivateKey(n,e,d,p,q)
            return (PrivateKey)
        except:
            QMessageBox.about(self, "Внимание", "Неправильный путь до ключа")
            return False

    def do_exit(self, line):
        exit(0)

if __name__ == "__main__":
    cli = Cli()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print ('завершение сеанса...')

