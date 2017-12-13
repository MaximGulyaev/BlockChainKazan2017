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
        print("Attention", "Error in file pathча")
        return False

class Cli(cmd.Cmd):
    accountSystemClass = None
    dataBaseAdapt = None
    CblockChain = None
    Cnetwork = None
    isAuth = False

    def __init__(self):
        cmd.Cmd.__init__(self,'\t')
        self.dataBaseAdapt = dataBaseAdapter.dataBaseAdapter()
        self.accountSystemClass = CAccountingSystem.CAccountingSystem(self.dataBaseAdapt)
        self.CblockChain = Block_chain.Blockchain()
        self.Cnetwork = network.network(self.CblockChain)
        self.CblockChain.InitAddNetWork(self.Cnetwork)
        self.prompt = "(not auth)> "
        self.intro  = "Welcome\nFor help enter 'help'"
        self.doc_header ="Available (for help on a specific command, enter 'help _command')"


    def default(self, line):
        '''
        Handler command, when not in list command

        :param line: no usable(but it's features cmd lib)
        :return: message with Error
        '''
        print ('Error in command. See help')


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
            print(consts.userNotExist)

    def do_logout(self,args):
        '''
        Handler command logout. User logout from account

        :param args: no usable(but it's features cmd lib)
        :return: user out from account
        '''
        self.accountSystemClass.logout()
        print(consts.userLogoutAtt)
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
        print(consts.createUserAtt)

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
            print(consts.errorInPath)
            return False

    def do_doExpert(self,argv):
        '''
        Handler command doExpert. User raises his rank to an expert

        :param argv:no usable(but it's features cmd lib)
        :return: message and unconfirmedTransaction in db
        '''
        if (self.isAuth):
            print( "Attention",
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
                print(consts.errorSomethingWentWrong)
        else:
            print(consts.erorLoginToNet)

    def do_downgrade(self,args):
        '''
         Handler command downgrade. The expert advances another expert on the decline
         Needed input arguments. Example : 'downgrade 999' 999 is idUser
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
                    currentUser = '==================\nUserId : {0}\nUsername : {1}\nBirthday : {2}\nStatus :{3}\nOrganization :{4}\n'\
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
                            print(consts.errorSomethingWentWrong)
                    else:
                        print('He will thank you')
        else:
            print(consts.erorLoginToNet)

    def do_createTransaction(self,args):
        if (self.isAuth):
            Transaction = {}
            datadict = {}
            datadict['name'] = input('Enter the name of event : ')
            datadict['date'] = input('Enter the date event : ')
            datadict['competence'] = input('Enter the competence event : ')
            datadict['rating'] = input('Enter the raiting event : ')
            datadict['info'] = input('Enter event details : ')
            autor = self.dataBaseAdapt.getUser(self.accountSystemClass.account['Address'])
            userList = []
            expertList = []
            expertList.append(autor)

            symbol = input("Do you want add user?Y/n ")
            symbol = symbol.upper()

            while symbol == 'Y':
                userId = input('Please enter userId ')
                user = self.dataBaseAdapt.getUserById(userId)
                status = 'User'
                if (user == None):
                    print(consts.userNotExist)
                    symbol = input("Yet add user?Y/n ")
                    symbol = symbol.upper()
                else:
                    if (user[consts.usersColumns.get('isExpert')] == 1):
                        status = 'Expert'
                    currentUser = '==================\nUserId : {0}\nUsername : {1}\nBirthday : {2}\nStatus :{3}\nOrganization :{4}\n'\
                        .format(user[consts.usersColumns.get('idUser')], user[consts.usersColumns.get('name')], user[consts.usersColumns.get('birthday')], status, user[consts.usersColumns.get('organization')] )
                    print(currentUser)
                    accept = input('Add this user?Y/n ')
                    accept = accept.upper()
                    if (accept == "Y"):
                        if ((user in userList) or (user in expertList)):
                             print("User in other list")
                        else:
                            print(consts.addUser)
                            userList.append(user)
                        symbol = input("Yet add user?Y/n ")
                        symbol = symbol.upper()
                    else:
                        print(consts.notAddUser)
                        symbol = input("Yet add user?Y/n ")
                        symbol = symbol.upper()


            symbol = input("Do you want add expert?Y/n ")
            symbol = symbol.upper()

            while symbol == 'Y':
                userId = input('Please enter expertId ')
                user = self.dataBaseAdapt.getUserById(userId)
                if (user == None):
                    print(consts.userNotExist)
                    symbol = input("Yet add expert?Y/n ")
                    symbol = symbol.upper()
                else:
                    status = 'Expert'
                    if (user[consts.usersColumns.get('isExpert')] == 1):
                        currentUser = '==================\nUserId : {0}\nUsername : {1}\nBirthday : {2}\nStatus :{3}\nOrganization :{4}\n'\
                            .format(user[consts.usersColumns.get('idUser')], user[consts.usersColumns.get('name')], user[consts.usersColumns.get('birthday')], status, user[consts.usersColumns.get('organization')] )
                        print(currentUser)
                        accept = input('Add this expert?Y/n ')
                        accept = accept.upper()
                        if (accept == "Y"):
                            if ((user in userList) or (user in expertList)):
                                print("User in other list")
                            else:
                                print(consts.addUser)
                                expertList.append(user)
                        else:
                            print(consts.notAddUser)
                        symbol = input("Yet add expert?Y/n ")
                        symbol = symbol.upper()
                    else:
                        currentUser = '==================\nUserId : {0}\nUsername : {1}\nBirthday : {2}\nStatus :{3}\nOrganization :{4}\n'\
                            .format(user[consts.usersColumns.get('idUser')], user[consts.usersColumns.get('name')], user[consts.usersColumns.get('birthday')], status, user[consts.usersColumns.get('organization')] )
                        print(currentUser)
                        print(consts.userNotExpert)

            datadict['users'] = userList
            datadict['experts'] = expertList

            Transaction['data'] = datadict
            Transaction['address'] = self.accountSystemClass.account['Address']
            Transaction['type'] = 5
            Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(
                self.accountSystemClass.account['PublicKey'])

            string = json.dumps(Transaction, sort_keys = True)
            signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
            Transaction['signature'] = signature
            if not (self.CblockChain.addNewTransactFromUser(Transaction)):
                print(consts.errorSomethingWentWrong)
        else:
            print(consts.erorLoginToNet)


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
                        print(consts.errorSomethingWentWrong)
        else:
            print(consts.erorLoginToNet)

    def do_getMyEvent(self,args):
        '''
        Handler command getMyEvent. User get list with your events,where he is expert and he is user

        :param args:no usable(but it's features cmd lib)
        :return: list with user event on console. No return value
        '''
        if (self.isAuth):
            addrUser = self.accountSystemClass.account.get('Address')
            list = self.dataBaseAdapt.getEventForUser(1,addrUser)
            if (len(list) == 0):
                print('Event as Expert : no events')
            else:
                print('Event as Expert')
                for element in list:
                    eventInfo = 'Name event : {0} \ndate : {1} \ncompetence : {2} \nraiting : {3} \ndata : {4}'.\
                        format( element[consts.eventsColumns.get('name')],element[consts.eventsColumns.get('date')],
                                element[consts.eventsColumns.get('competence')],element[consts.eventsColumns.get('raiting')],element[consts.eventsColumns.get('data')])
                    print('==========================================================')
                    print(eventInfo)
            list = self.dataBaseAdapt.getEventForUser(0,addrUser)
            print('==========================================================')
            if (len(list) == 0):
                print('Event as User : no events')
            else:
                print('Event as User')
                for element in list:
                    eventInfo = 'Name event : {0} \ndate : {1} \ncompetence : {2} \nraiting : {3} \n{4}'.\
                        format( element[consts.eventsColumns.get('name')],element[consts.eventsColumns.get('date')],
                                element[consts.eventsColumns.get('competence')],element[consts.eventsColumns.get('raiting')],element[consts.eventsColumns.get('data')])
                    print('==========================================================')
                    print(eventInfo)
            print('==========================================================')
        else:
            print(consts.erorLoginToNet)

    def do_getAllUsers(self,args):
        '''
        Handler command getAllUsers. User received list with all user

        :param args: args:no usable(but it's features cmd lib)
        :return: list with all users in network
        '''
        if (self.isAuth):
            userList = self.dataBaseAdapt.getUserList()
            if (len(userList) == 0):
                print('no users')
            else:
                for user in userList:
                    status = 'User'
                    if (user[consts.usersColumns.get('isExpert')] == 1):
                        status = 'Expert'
                    currentUser = '==================\nUserId : {0}\nUsername : {1}\nBirthday : {2}\nStatus :{3}\nOrganization :{4}\n' \
                        .format(user[consts.usersColumns.get('idUser')], user[consts.usersColumns.get('name')],
                                user[consts.usersColumns.get('birthday')], status,
                                user[consts.usersColumns.get('organization')])
                    print(currentUser)
        else:
            print(consts.erorLoginToNet)


    def do_exit(self, line):
        '''
        Exit of program. No parametrs

        :param line:no usable(but it's features cmd lib)
        :return:
        '''
        exit(0)

if __name__ == "__main__":
    cli = Cli()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print ('Exit')

