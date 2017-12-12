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
import consts

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
        user = self.dataBaseAdapt.getUserById('1')
        print(user)

        if (len(args) == None):
            print('sdfsdfsdfsdf')
        else:
            args = args.split()[0]
            print(args)
        """hello - выводит 'hello world' на экран"""

        print ('hello world')

    def default(self, line):
        '''
        Handler command, when not in list command

        :param line: no usable(but it's features cmd lib)
        :return: message with Error
        '''
        print ('Error in command. See help')

    def do_getAllEvents(self, args):
        #print('Введите свое имя')
        name = input('Введите свое имя')
        #print (name)
        #print (args)

    def do_login(self, args):
        '''
        Handler command login. It's user logging

        :param args: no usable(but it's features cmd lib)
        this module asks path to user Private key
        :return: user enter to your account or Error
        '''
        pathToPrivateKey = input('Please enter path to file with your private key:\n ')
        privateKey = getPrivateKeyFromFile(pathToPrivateKey)
        if not (privateKey):
            print('Error. Not found your private key or incorrect')
            return False

        if (self.accountSystemClass.authorization(privateKey)):
            self.CblockChain.setPrivateKey(privateKey)
            self.prompt = "> "
            self.isAuth = True
            name = self.accountSystemClass.account.get('Name')
            print("Hello ", name)
        else:
            print("Attention", "User not exist")

    def do_logout(self,args):
        '''
        Handler command logout. User logout from account

        :param args: no usable(but it's features cmd lib)
        :return: user out from account
        '''
        self.accountSystemClass.logout()
        print("Attention", "You are logout ")
        self.prompt = "(not auth)> "
        self.isAuth = False

    def generatePrivateKey(self):
        '''
        This method generate private key for user

        :return: absolute path to file with private key
        '''
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
        '''
        Handler command createNewUser. User passes registration procedure

        :param argv:no usable(but it's features cmd lib)
        :return: user create account. User's account
        '''
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
        '''
        This method return private key read from file

        :param fname: it's name file = path to file
        :return: private key from file or False(Error)
        '''
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
            print("Attention", "Error in file path")
            return False

    def do_doExpert(self,argv):
        '''
        Handler command doExpert. User raises his rank to an expert

        :param argv:no usable(but it's features cmd lib)
        :return: message and unconfirmedTransaction in db
        '''
        if (self.isAuth):
            print(self, "Attention",
                              "You apply for a Status Change to the 'Expert' status. "\
                              "The application will be reviewed by experts within 24 hours" + \
                              "the time for which the application is added to the chain."\
                                      "If after this time your status does not change, "\
                                      "then the application denied.")
            Transaction = {}
            dict = {}
            dict['address'] = self.accountSystemClass.account['Address']
            Transaction['address'] = self.accountSystemClass.account['Address']
            Transaction['type'] = 1
            Transaction['data'] = dict
            Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(self.accountSystemClass.account['PublicKey'])
            string = json.dumps(Transaction, sort_keys = True)
            signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
            Transaction['signature'] = signature
            if not (self.CblockChain.addNewTransactFromUser(Transaction)):
                print("Error", "Something went wrong")
        else:
            print("Please login to net")

    def do_downgrade(self,args):
        '''
         Handler command downgrade. The expert advances another expert on the decline

         :param argv: id user
         :return: message and unconfirmedTransaction in db
         '''
        if (self.isAuth):
            if( len(args) == 0):
                print("Error", "Needed input arguments. Example : 'downgrade 999'. 999 is idUser")
            else:
                index = args.split()[0]

                user = self.dataBaseAdapt.getUserById(index)

                if ((user == None) or  len(user)== 0 ):
                    print("Error", "User not found")
                else:
                    status = 'User'
                    if (user[consts.usersColumns.get('isExpert')] == 1):
                        status = 'Expert'
                    currentUser = '==================\nUserId : {0}\nUsername : {1}\n Birthday : {2}\n Status :{3}\n Organization :{4}\n'\
                        .format(user[consts.usersColumns.get('idUser')], user[consts.usersColumns.get('name')], user[consts.usersColumns.get('birthday')], status, user[consts.usersColumns.get('organization')] )
                    print(currentUser)
                    symbol = input('Are you sure you want to demote this user?y/n')
                    if ((symbol == 'Y') or (symbol == 'y') or (symbol == 'д') or (symbol == 'Д')):
                        Transaction = {}
                        datadict = {}
                        datadict['address'] = user[consts.usersColumns.get('addres')]
                        Transaction['data'] = datadict
                        Transaction['address'] = self.accountSystemClass.account['Address']
                        Transaction['type'] = 2
                        Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(self.accountSystemClass.account['PublicKey'])
                        string = json.dumps(Transaction, sort_keys = True)
                        signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
                        Transaction['signature'] = signature
                        if not (self.CblockChain.addNewTransactFromUser(Transaction)):
                            print("Error", "Something went wrong")
                    else:
                        print('He will thank you')
        else:
            print("Please login to net")

    def do_confirm(self,args):
        if (self.isAuth):
            if (len(args) < 2):
                print("Error", "Needed input arguments. Example : 'confirm -e 9913' or 'confirm -u 1'.\n"
                               "-e is event\n -u is user downgrade or user doExpert\n, numbers is appropriate id")
            else:
                Transaction = {}
                datadict = {}
                Transaction['address'] = self.accountSystemClass.account['Address']
                Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(
                    self.accountSystemClass.account['PublicKey'])
                typeQuerry = args.split()[0]
                id = args.split()[1]
                requestMode = 0
                if (typeQuerry == '-e'):
                    requestMode = 1
                    #0 == -u
                if (requestMode == 0):
                    requestList = self.dataBaseAdapt.getRequestList()
                    if (self.dataBaseAdapt.getRequestList() == None):
                        return False

                    Transaction['type'] = 3
                    datadict['idRequest'] = requestList[id][
                    consts.requestColumns.get('idRequest')]
                    Transaction['data'] = datadict
                    string = json.dumps(Transaction, sort_keys=True)
                    signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
                    Transaction['signature'] = signature
                    if not (self.CblockChain.addNewTransactFromUser(Transaction)):
                        print("Error", "Something went wrong")
                if (requestMode == 1):
                    requestList = self.dataBaseAdapt.getEventUpdateList()
                    if (requestList == None):
                        return False
                    Transaction['type'] = 4
                    datadict['updateIndex'] = requestList[id][
                        consts.eventsUpdateColumns.get('updateIndex')]
                    datadict['idEvent'] = requestList[id][
                        consts.eventsUpdateColumns.get('idEvent')]
                    Transaction['data'] = datadict
                    string = json.dumps(Transaction, sort_keys=True)
                    signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
                    Transaction['signature'] = signature
                    if not (self.CblockChain.addNewTransactFromUser(Transaction)):
                        print("Error", "Something went wrong")
        else:
            print("Please login to net")

    def do_exit(self, line):
        exit(0)

if __name__ == "__main__":
    cli = Cli()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print ('завершение сеанса...')

