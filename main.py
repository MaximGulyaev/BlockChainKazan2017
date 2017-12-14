import sys

import MainForm
import CAccountingSystem
import dataBaseAdapter
import Block_chain
import  network
import PyQt5
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLabel, QGridLayout, QWidget, QDesktopWidget, QFileDialog
from PyQt5 import QtCore
import rsa
import os
import json
import consts
import threading
from collections import OrderedDict

class GUI_form(QMainWindow, MainForm.Ui_MainWindow):
    dataBaseAdapt = dataBaseAdapter.dataBaseAdapter()
    accountSystemClass = CAccountingSystem.CAccountingSystem(dataBaseAdapt)
    CblockChain = Block_chain.Blockchain()
    Cnetwork = network.network(CblockChain)
    CblockChain.InitAddNetWork(Cnetwork)
    _threadListener = threading.Thread(name="Listen", target=Cnetwork.receiveMessage)
    _threadListener.start()
    _threadMiner = threading.Thread(name="Miner", target=CblockChain.startMine)
    _threadMiner.start()
    _threadLenChecker = threading.Thread(name="LebChecker", target=Cnetwork.lenCheckerNeighbourhood)
    _threadLenChecker.start()



    _EventInfochoseIndex = None
    _ChangeEventChoseIndex = None
    _EventInfoShownListTuple = []
    _selectItemRequest_index = None
    _ChangeEventChoseEventIndex = None

    _EventCreateUserList = []
    _EventCreateExpertList = []
    _ChangeEventExpertsList = []
    _ChangeEventUserList = []
    _EventCreateTableMode = None
    _ChangeEventTableMode = None
    _Request_mode = 0
    _Request_listOfChangeEvent = []
    _Request_listOfChangeUserStat = []

    def __init__(self, parent = None):
        super().__init__()
        self.setupUi(self)
        self.pb_auth_registration.clicked.connect(self.pb_register_clicked)
        self.pb_auth_Login.clicked.connect(self.pb_auth_Login_clicked)

        self.pb_registration_GoToAuth.clicked.connect(self.Show_authList)
        self.pb_main_Exit.clicked.connect(self.close)
        self.pb_main_Exit_2.clicked.connect(self.close)
        self.pb_main_Exit_3.clicked.connect(self.close)

        self.pb_menu_aboutAccount.clicked.connect(self.change_Menu)
        self.pb_menu_eventInfo.clicked.connect(self.change_Menu)
        self.pb_menu_createEvent.clicked.connect(self.change_Menu)
        self.pb_menu_changeEvent.clicked.connect(self.change_Menu)
        self.pb_menu_unconfirmedRequest.clicked.connect(self.change_Menu)
        self.pb_menu_lower.clicked.connect(self.change_Menu)
        self.pb_mainLogOut.clicked.connect(self.change_Menu)
        self.pb_menu_UsersInfo.clicked.connect(self.change_Menu)

        self.pb_generatePrivKey.clicked.connect(self.generatePrivateKey)
        self.pb_auth_choseFileWithKey.clicked.connect(self.pb_auth_choseFileWithKey_clicked)
        self.cb_eventInfo_ChoseEvent.currentIndexChanged.connect(self.cb_eventInfo_ChoseEvent_currentIndexChanged)
        self.cb_changeEvent_ChoseEvent.currentIndexChanged.connect(self.cb_changeEvent_ChoseEvent_currentIndexChanged)
        self.pb_EventInfo_getExpertList.clicked.connect(self.pb_EventInfo_getExpertList_clicked)
        self.pb_EventInfo_getUserList.clicked.connect(self.pb_EventInfo_getUserList_clicked)
        self.pb_createEvent_getExpertList.clicked.connect(self.pb_createEvent_getExpertList_clicked)
        self.pb_createEvent_getUserList.clicked.connect(self.pb_createEvent_getUserList_clicked)
        self.pb_createEvent_addUer.clicked.connect(self.pb_createEvent_addUer_clicked)
        self.pb_createEvent_deleteUser.clicked.connect(self.pb_createEvent_deleteUser_clicked)
        self.pb_changeEvent_addUer.clicked.connect(self.pb_changeEvent_addUer_clicked)
        self.pb_changeEvent_deleteUser.clicked.connect(self.pb_changeEvent_deleteUser_clicked)
        self.pb_changeEvent_getExpertList.clicked.connect(self.pb_changeEvent_getExpertList_clicked)
        self.pb_changeEvent_getUserList.clicked.connect(self.pb_changeEvent_getUserList_clicked)
        self.cb_request_mode.currentIndexChanged.connect(self.cb_request_mode_currentIndexChanged)
        self.tw_requestList.itemClicked.connect(self.tw_requestList_selectitem)


        self.pb_changeEvent_PushCreateEventRequest.clicked.connect(self.pb_changeEvent_PushChangeEventRequest_clicked)
        self.pb_makeRequestToBeExpert.clicked.connect(self.pb_makeRequestToBeExpert_clicked)
        self.pb_createEvent_PushCreateEventRequest.clicked.connect(self.pb_createEvent_PushCreateEventRequest_clicked)
        self.tw_lowerRequest_UserList.itemClicked.connect(self.tw_lowerRequest_UserList_selecteditem)
        self.pb_sendRegistReqv.clicked.connect(self.pb_sendRegistReqv_clicked)  
        self.pb_lowerRequest_PushRequest.clicked.connect(self.pb_lowerRequest_PushRequest_clicked)
        self.pb_request_confirmRequest.clicked.connect(self.pb_request_confirmRequest_clicked)

        self.pb_menu_StartMine.clicked.connect(self.pb_menu_StartMine_clicked)



        self.MainPages.setCurrentIndex(0)



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
        ex.cb_registr_choseFileWithPrivateKey.addItem('PrivateKey_' + str(s))
        QMessageBox.about(self, "Внимание", "Ключ создан в папке с программой. Пожалуйста сохраните его")

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

    def change_Menu(self):
        btn_name = self.sender().objectName()
        if (btn_name == 'pb_menu_aboutAccount' and True):
            self.SW_menu.setCurrentIndex(0)
            return True
        if (btn_name == 'pb_mainLogOut'):
            self.MainPages.setCurrentIndex(0)
        if (btn_name == 'pb_menu_eventInfo' and True):
            self.SW_menu.setCurrentIndex(1)
            return True
        if (btn_name == 'pb_menu_createEvent' and True):
            self.SW_menu.setCurrentIndex(2)
            return True
        if (btn_name == 'pb_menu_changeEvent' and True):
            self.SW_menu.setCurrentIndex(3)
            return True
        if (btn_name == 'pb_menu_unconfirmedRequest' and True):
            self.SW_menu.setCurrentIndex(4)
            return True
        if (btn_name == 'pb_menu_lower' and True):
            self.SW_menu.setCurrentIndex(5)
            return True
        if (btn_name == 'pb_menu_UsersInfo'):
            self.SW_menu.setCurrentIndex(6)
            return True
        if (btn_name == 'pushButton'):
            self.SW_menu.setCurrentIndex(7)
            return True

    def LoadMenu(self):
        if self.accountSystemClass.account['isExpert']:
            m = "Expert"
            ex.wdgt_expertMenu.setVisible(True)
        else:
            m = "User"
        self.lbl_imya.setText(self.accountSystemClass.account['Name'])
        self.lbl_organization.setText(self.accountSystemClass.account['Organization'])
        self.lbl_adress.setText(self.accountSystemClass.account['Address'])
        self.lbl_dateOfBirth.setText(self.accountSystemClass.account['Birthday'])
        self.lbl_isExpert.setText(m)
        return True

    def Show_authList(self):
        self.MainPages.setCurrentIndex(0)
        return True

    def pb_register_clicked(self):
        self.MainPages.setCurrentIndex(1)
        return True

    def pb_sendRegistReqv_clicked(self):
        Transaction = {}
        datadict = {}
        datadict['organization'] = self.le_organization.text()
        datadict['name'] = self.le_imya.text()
        datadict['birthday'] = self.le_dateOfBirth.text()

        Transaction['data'] = datadict
        Transaction['type'] = 0
        path = self.cb_registr_choseFileWithPrivateKey.currentText()

        if not os.path.exists('keys/' + path) or path == "":
            QMessageBox.about(self, "Внимание", "некорректный выбор файла")
            return False
        path = 'keys/' + path
        privateKey = self.getPrivateKeyFromFile(path)
        Transaction['address'] = self.accountSystemClass.publicKeyToAddress(privateKey)
        Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(privateKey)

        string = json.dumps(Transaction, sort_keys = True)
        signature = self.accountSystemClass.createSingature(privateKey, string)
        Transaction['signature'] = signature
        if not (self.CblockChain.addNewTransactFromUser(Transaction)):
            QMessageBox.about(self, "Внимание", "Артур, что-то не так")
            return False

        QMessageBox.about(self, "Внимание", "Вы отправили запрос на регистрацию. "
                                            "Пожалуйста Ожидайте, пока кто-то из зарегистрированных пользователей "
                                            "системы не подтвердит вашу регистрацию")


    def pb_auth_Login_clicked(self):
        privateKey = self.getPrivateKeyFromFile(self.lbl_auth_pathToSecretKey.text())
        if not (privateKey):
            return False

        if (self.accountSystemClass.authorization(privateKey)):
            self.LoadMenu()
            self.MainPages.setCurrentIndex(2)
            self.CblockChain.setPrivateKey(privateKey)
            #if not self._threadMiner.is_alive():
            #    self._threadMiner.start()
        else:
            QMessageBox.about(self, "Внимание", "Несуществующий пользователь")

    def pb_auth_choseFileWithKey_clicked(self):
        text = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        self.lbl_auth_pathToSecretKey.setText(text)

    def pb_makeRequestToBeExpert_clicked(self):
        QMessageBox.about(self, "Внимание",
                          "Вы подали заявку на Смену статуса в состояние 'Эксперта'. \n" + \
                          "Заявка будет рассмотрена экспертами в течение 24 часов + " +\
                          "время, за которое заявка добавится в цепочку.\n" +\
                          "Если по истечении этого времени ваш статус не изменится, " +
                          "то в заявке вам отказано.")
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
            QMessageBox.about(self, "Внимание", "Ошибка в обработке транзакции!")
        # ToDo Транзакция добавляется

    def pb_lowerRequest_PushRequest_clicked(self):
        self.tw_lowerRequest_UserList.currentRow()
        if (self.tw_lowerRequest_UserList.currentItem() == None):
            return False
        m = self.tw_lowerRequest_UserList.currentItem().row()
        index = self.tw_lowerRequest_UserList.item(m, 0).text()
        user = self.dataBaseAdapt.getUserById(index)

        Transaction = {}
        datadict = {}
        datadict['address'] =  user[consts.usersColumns.get('addres')]
        Transaction['data'] = datadict
        Transaction['address'] = self.accountSystemClass.account['Address']
        Transaction['type'] = 2
        Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(self.accountSystemClass.account['PublicKey'])
        string = json.dumps(Transaction, sort_keys=True)
        signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
        Transaction['signature'] = signature
        if not (self.CblockChain.addNewTransactFromUser(Transaction)):
            QMessageBox.about(self, "Внимание", "Артур, что-то не так")
        # ToDo Транзакция добавляется

    def pb_request_confirmRequest_clicked(self):
        Transaction = {}
        datadict = {}
        Transaction['address'] = self.accountSystemClass.account['Address']
        Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(
            self.accountSystemClass.account['PublicKey'])
        if (self._Request_mode == 0):
            if (self._Request_listOfChangeUserStat == None):
                return False
            Transaction['type'] = 3
            datadict['idRequest'] = self._Request_listOfChangeUserStat[self._selectItemRequest_index][
            consts.requestColumns.get('idRequest')]
            Transaction['data'] = datadict
            string = json.dumps(Transaction, sort_keys=True)
            signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
            Transaction['signature'] = signature
            if not (self.CblockChain.addNewTransactFromUser(Transaction)):
                QMessageBox.about(self, "Внимание", "АФИПКА")
        if (self._Request_mode == 1):
            if (self._Request_listOfChangeEvent == None):
                return False
            Transaction['type'] = 4
            datadict['updateIndex'] = self._Request_listOfChangeEvent[self._selectItemRequest_index][
                consts.eventsUpdateColumns.get('updateIndex')]
            datadict['idEvent'] = self._Request_listOfChangeEvent[self._selectItemRequest_index][
                consts.eventsUpdateColumns.get('idEvent')]
            Transaction['data'] = datadict
            string = json.dumps(Transaction, sort_keys=True)
            signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
            Transaction['signature'] = signature
            if not (self.CblockChain.addNewTransactFromUser(Transaction)):
                QMessageBox.about(self, "Внимание", "АФИПКА")

    def cb_changeEvent_ChoseEvent_currentIndexChanged(self):
            self._ChangeEventChoseEventIndex = self.cb_changeEvent_ChoseEvent.currentIndex()
            self.le_changeEvent_name.setText(str(self._EventInfoShownListTuple[self._ChangeEventChoseEventIndex][consts.eventsColumns.get('name')]))
            self.le_changeEvent_date.setText(str(self._EventInfoShownListTuple[self._ChangeEventChoseEventIndex][consts.eventsColumns.get('date')]))
            self.le_changeEvent_competence.setText(str(self._EventInfoShownListTuple[self._ChangeEventChoseEventIndex][consts.eventsColumns.get('competence')]))
            self.te_changeEvent_Info.setText(str(self._EventInfoShownListTuple[self._ChangeEventChoseEventIndex][consts.eventsColumns.get('data')]))
            self._ChangeEventUserList = []
            self._ChangeEventExpertsList = []
            self.clearTableWdiget(self.tw_changeEvent_addedUserList)
            self.clearTableWdiget(self.tw_changeEvent_UserList)

            ExpertsListShort = self.dataBaseAdapt.getEventExpertList(
                self._EventInfoShownListTuple[self._ChangeEventChoseEventIndex][consts.eventsColumns.get('idEvent')])
            for element in ExpertsListShort:
                FullUser = self.dataBaseAdapt.getUser(element[consts.groupColumns.get('addres')])
                if (FullUser != None):
                    self._ChangeEventExpertsList.append(FullUser)
            UserListShort = self.dataBaseAdapt.getEventUserList(
                self._EventInfoShownListTuple[self._ChangeEventChoseEventIndex][consts.eventsColumns.get('idEvent')])
            for element in UserListShort:
                FullUser = self.dataBaseAdapt.getUser(element[consts.groupColumns.get('addres')])
                if (FullUser != None):
                    self._ChangeEventUserList.append(FullUser)

    def pb_changeEvent_deleteUser_clicked(self):
        self.tw_changeEvent_addedUserList.currentRow()
        if (self.tw_changeEvent_addedUserList.currentItem() == None):
            return False
        m = self.tw_changeEvent_addedUserList.currentItem().row()
        index = self.tw_changeEvent_addedUserList.item(m, 0).text()
        user = self.dataBaseAdapt.getUserById(index)
        if self._ChangeEventChoseIndex:
            self._ChangeEventExpertsList.remove(user)
            self.pb_changeEvent_getExpertList_clicked()
        else:
            self._ChangeEventUserList.remove(user)
            self.pb_changeEvent_getUserList_clicked()

    def pb_changeEvent_addUer_clicked(self):
        self.tw_changeEvent_UserList.currentRow()
        if (self.tw_changeEvent_UserList.currentItem() == None):
            return False
        m = self.tw_changeEvent_UserList.currentItem().row()
        index = self.tw_changeEvent_UserList.item(m, 0).text()
        user = self.dataBaseAdapt.getUserById(index)
        if not (user == None):
            if self._ChangeEventChoseIndex and not (user in self._ChangeEventExpertsList):
                    self._ChangeEventExpertsList.append(user)
                    self.pb_changeEvent_getExpertList_clicked()
            if not self._ChangeEventChoseIndex and not (user in self._ChangeEventUserList):
                    self._ChangeEventUserList.append(user)
                    self.pb_changeEvent_getUserList_clicked()

    def pb_changeEvent_getUserList_clicked(self):
        AllUserList = self.dataBaseAdapt.getUserList()
        self.fillUserTableWidget_id_name_organization(self.tw_changeEvent_UserList, AllUserList)
        self.fillUserTableWidget_id_name_organization(self.tw_changeEvent_addedUserList, self._ChangeEventUserList)
        self._ChangeEventChoseIndex = 0

    def pb_changeEvent_getExpertList_clicked(self):
        AllExpertList = self.dataBaseAdapt.getUserListByCriterion(1)
        self.fillUserTableWidget_id_name_organization(self.tw_changeEvent_UserList, AllExpertList)
        self.fillUserTableWidget_id_name_organization(self.tw_changeEvent_addedUserList, self._ChangeEventExpertsList)
        self._ChangeEventChoseIndex = 1

    def pb_changeEvent_PushChangeEventRequest_clicked(self):
        Transaction = {}
        datadict = {}
        datadict['idEvent'] = self._EventInfoShownListTuple[self._ChangeEventChoseEventIndex][consts.eventsColumns.get('idEvent')]
        datadict['name'] = self.le_changeEvent_name.text()
        datadict['date'] = self.le_changeEvent_date.text()
        datadict['competence'] = self.le_changeEvent_competence.text()
        datadict['rating'] = 0
        datadict['info'] = self.le_changeEvent_date.text()
        datadict['users'] = self._ChangeEventUserList
        datadict['experts'] = self._ChangeEventExpertsList

        Transaction['data'] = datadict
        Transaction['address'] = self.accountSystemClass.account['Address']
        Transaction['type'] = 6
        Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(self.accountSystemClass.account['PublicKey'])

        string = json.dumps(Transaction, sort_keys=True)
        signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
        Transaction['signature'] = signature
        if not (self.CblockChain.addNewTransactFromUser(Transaction)):
                QMessageBox.about(self, "Внимание", "Артур, что-то не так")
        # ToDo Транзакция добавляется

    def cb_eventInfo_ChoseEvent_currentIndexChanged(self):
       # try:
        if len(self._EventInfoShownListTuple) == 0:
            return False
        self._EventInfochoseIndex = self.cb_eventInfo_ChoseEvent.currentIndex()

        self.lbl_eventInfo_eventName.setText(str(self._EventInfoShownListTuple[self._EventInfochoseIndex][consts.eventsColumns.get('name')]))
        self.lbl_eventInfo_eventDate.setText(str(self._EventInfoShownListTuple[self._EventInfochoseIndex][consts.eventsColumns.get('date')]))
        self.lbl_eventInfo_eventCreator.setText(str(self._EventInfoShownListTuple[self._EventInfochoseIndex][consts.eventsColumns.get('creator')]))
        self.lbl_eventInfo_EventCompetence.setText(str(self._EventInfoShownListTuple[self._EventInfochoseIndex][consts.eventsColumns.get('competence')]))
        self.lbl_eventInfo_idevent.setText(str(self._EventInfoShownListTuple[self._EventInfochoseIndex][consts.eventsColumns.get('idEvent')]))
        self.tb_event_info.setText(str(self._EventInfoShownListTuple[self._EventInfochoseIndex][consts.eventsColumns.get('data')]))
        self.clearTableWdiget(self.tw_eventinfo_userlist)
      #  except:
      #      pass

    def pb_EventInfo_getExpertList_clicked(self):
        try:
            id = self._EventInfoShownListTuple[self._EventInfochoseIndex][consts.eventsColumns.get('idEvent')]
            ExpertList = self.dataBaseAdapt.getEventExpertList(id)
            FullExpertList = []
            for element in ExpertList:
                FullUser = self.dataBaseAdapt.getUser(element[consts.groupColumns.get('addres')])
                if (FullUser != None):
                    FullExpertList.append(FullUser)
            self.fillUserTableWidget_id_name_organization(self.tw_eventinfo_userlist, FullExpertList)
        except:
            pass

    def pb_EventInfo_getUserList_clicked(self):
        try:
            id = self._EventInfoShownListTuple[self._EventInfochoseIndex][consts.eventsColumns.get('idEvent')]
            UsersList = self.dataBaseAdapt.getEventUserList(id)
            FullUserList = []
            for element in UsersList:
                FullUser = self.dataBaseAdapt.getUser(element[consts.groupColumns.get('addres')])
                if (FullUser != None):
                    FullUserList.append(FullUser)

            self.fillUserTableWidget_id_name_organization(self.tw_eventinfo_userlist, FullUserList)
        except:
            pass

    def pb_createEvent_getExpertList_clicked(self):
        AllExpertList = self.dataBaseAdapt.getUserListByCriterion(1)
        self.fillUserTableWidget_id_name_organization(self.tw_createEvent_UserList, AllExpertList)
        self.fillUserTableWidget_id_name_organization(self.tw_createEvent_addedUserList, self._EventCreateExpertList)
        self._EventInfochoseIndex = 1

    def pb_createEvent_getUserList_clicked(self):
        AllUserList = self.dataBaseAdapt.getUserListByCriterion(0)
        self.fillUserTableWidget_id_name_organization(self.tw_createEvent_UserList, AllUserList)
        self.fillUserTableWidget_id_name_organization(self.tw_createEvent_addedUserList, self._EventCreateUserList)
        self._EventInfochoseIndex = 0

    def pb_createEvent_addUer_clicked(self):
       self.tw_createEvent_UserList.currentRow()
       if (self.tw_createEvent_UserList.currentItem() == None):
           return False
       m = self.tw_createEvent_UserList.currentItem().row()
       index = self.tw_createEvent_UserList.item(m, 0).text()
       user = self.dataBaseAdapt.getUserById(index)
       if not (user == None):
           if self._EventInfochoseIndex and not (user in self._EventCreateExpertList):
                    self._EventCreateExpertList.append(user)
                    self.pb_createEvent_getExpertList_clicked()
           if not self._EventInfochoseIndex and not (user in self._EventCreateUserList):
                   self._EventCreateUserList.append(user)
                   self.pb_createEvent_getUserList_clicked()

    def pb_createEvent_deleteUser_clicked(self):
        self.tw_createEvent_addedUserList.currentRow()
        if (self.tw_createEvent_addedUserList.currentItem() == None):
            return False
        m = self.tw_createEvent_addedUserList.currentItem().row()
        index = self.tw_createEvent_addedUserList.item(m, 0).text()
        user = self.dataBaseAdapt.getUserById(index)
        if self._EventInfochoseIndex:
            self._EventCreateExpertList.remove(user)
            self.pb_createEvent_getExpertList_clicked()
        else:
            self._EventCreateUserList.remove(user)
            self.pb_createEvent_getUserList_clicked()

    def pb_createEvent_PushCreateEventRequest_clicked(self):
        Transaction = {}
        datadict = {}
        datadict['name'] = self.le_createEvent_name.text()
        datadict['date'] = self.le_createEvent_date.text()
        datadict['competence'] = self.le_createEvent_competence.text()
        datadict['info'] = self.te_createEvent_info.toPlainText()
        datadict['users'] = self._EventCreateUserList
        autor = self.dataBaseAdapt.getUser(self.accountSystemClass.account['Address'])
        if not (autor in self._EventCreateExpertList):
            self._EventCreateExpertList.append(autor)
        datadict['experts'] = self._EventCreateExpertList

        Transaction['data'] = datadict
        Transaction['address'] = self.accountSystemClass.account['Address']
        Transaction['type'] = 5
        Transaction['publicKey'] = self.accountSystemClass.publicKeyToString(self.accountSystemClass.account['PublicKey'])

        string = json.dumps(Transaction, sort_keys=True)
        signature = self.accountSystemClass.createSingature(self.accountSystemClass.account['PrivateKey'], string)
        Transaction['signature'] = signature
        if not (self.CblockChain.addNewTransactFromUser(Transaction)):
            QMessageBox.about(self, "Внимание", "Артур, что-то не так")
        # ToDo Транзакция добавляется

    def tw_lowerRequest_UserList_selecteditem(self):
        #try:
            self.tw_lowerRequest_UserList.currentRow()
            m = self.tw_lowerRequest_UserList.currentItem().row()
            index = self.tw_lowerRequest_UserList.item(m, 0).text()
            user = self.dataBaseAdapt.getUserById(index)
            self.lbl_lowerRequest_Address.setText(user[consts.usersColumns.get('addres')])
            self.lbl_lowerRequest_Name.setText(user[consts.usersColumns.get('name')])
            self.lbl_lowerRequest_Birthday.setText(str(user[consts.usersColumns.get('birthday')]))
            self.lbl_lowerRequest_organization.setText(user[consts.usersColumns.get('organization')])
        #except:
        #    pass

    def cb_request_mode_currentIndexChanged(self):
        self.clearTableWdiget(self.tw_requestList)
        self._Request_listOfChangeEvent = self.dataBaseAdapt.getEventUpdateList()
        self._Request_listOfChangeUserStat = self.dataBaseAdapt.getRequestList()

        i = 0
        index = self.cb_request_mode.currentIndex()
        self._Request_mode = self.cb_request_mode.currentIndex()
        if(index == 0) and self._Request_listOfChangeUserStat != None and len(self._Request_listOfChangeUserStat):
            if (len(self._Request_listOfChangeUserStat) == 0):
                self.tw_requestList.setRowCount(0)
                return False
            self.tw_requestList.setRowCount(len(self._Request_listOfChangeUserStat))
            for element in self._Request_listOfChangeUserStat:
                self.tw_requestList.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(
                    str(element[consts.requestColumns.get('idRequest')])))
                self.tw_requestList.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(self.dataBaseAdapt.getUser(element[consts.requestColumns.get('addresTo')])[consts.usersColumns.get('name')]))
                if (element[consts.requestColumns.get('addresTo')] == element[consts.requestColumns.get('addresFrom')]):
                    self.tw_requestList.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem("Повышение"))
                else:
                    self.tw_requestList.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem("Понижение"))
                i += 1

        if (index  == 1) and len(self._Request_listOfChangeEvent):
            if (len(self._Request_listOfChangeEvent) == 0):
                self.tw_requestList.setRowCount(0)
                return False
            self.tw_requestList.setRowCount(len(self._Request_listOfChangeEvent))
            for element in self._Request_listOfChangeEvent:
                self.tw_requestList.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(
                    str(element[consts.eventsUpdateColumns.get('idEvent')])))
                self.tw_requestList.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(element[consts.eventsUpdateColumns.get('name')]))
                self.tw_requestList.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(element[consts.eventsUpdateColumns.get('data')]))
                i += 1
        self.tw_requestList.resizeColumnsToContents()
        self.tb_request_before.setText(" ")
        self.tb_request_after.setText(" ")

    def tw_requestList_selectitem(self):
        self.tw_requestList.currentRow()
        m = self.tw_requestList.currentItem().row()
        self._selectItemRequest_index = m
        string = " "
        if (self.cb_request_mode.currentIndex() == 1):
            string = 'name: ' + str(self._Request_listOfChangeEvent[m][consts.eventsUpdateColumns.get('name')]) + '\n' + \
                     'data: ' + str(self._Request_listOfChangeEvent[m][consts.eventsUpdateColumns.get('data')]) + '\n' + \
                     'date: ' + str(self._Request_listOfChangeEvent[m][consts.eventsUpdateColumns.get('date')]) + '\n' + \
                     'competence: ' + str(self._Request_listOfChangeEvent[m][consts.eventsUpdateColumns.get('competence')]) + '\n' + \
                     'idEvent: ' + str(self._Request_listOfChangeEvent[m][consts.eventsUpdateColumns.get('idEvent')]) + '\n' + \
                     'Users: ' + '\n'
            UserList = self.dataBaseAdapt.getEventUpdateUserList(self._Request_listOfChangeEvent[m][consts.eventsUpdateColumns.get('idUnconfirmedUpdate')])
            if (UserList != None):
                if (len(UserList)):
                    for element in UserList:
                        User = self.dataBaseAdapt.getUser(element[consts.groupColumns.get('addres')])
                        if not(User == None):
                            string += User[consts.usersColumns.get('name')] + '  ' + \
                                      User[consts.usersColumns.get('organization')] + '\n'
            string += 'Experts: ' + '\n'
            ExpertList = self.dataBaseAdapt.getEventUpdateExpertList(self._Request_listOfChangeEvent[m][consts.eventsUpdateColumns.get('idUnconfirmedUpdate')])
            if (ExpertList != None):
                if (len(ExpertList)):
                    for element in ExpertList:
                        User = self.dataBaseAdapt.getUser(element[consts.groupColumns.get('addres')])
                        if not(User == None):
                            string += User[consts.usersColumns.get('name')] + '  ' + \
                                      User[consts.usersColumns.get('organization')] + '\n'
            self.tb_request_after.setText(string)

            EventWantToChange = self.dataBaseAdapt.getEvent(self._Request_listOfChangeEvent[m][consts.eventsUpdateColumns.get('idEvent')])

            string = 'name: ' + str(
                EventWantToChange[consts.eventsColumns.get('name')]) + '\n' + \
                     'data: ' + str(
                EventWantToChange[consts.eventsColumns.get('data')]) + '\n' + \
                     'date: ' + str(
                EventWantToChange[consts.eventsColumns.get('date')]) + '\n' + \
                     'competence: ' + str(
                EventWantToChange[consts.eventsColumns.get('competence')]) + '\n' + \
                     'idEvent: ' + str(
                EventWantToChange[consts.eventsColumns.get('idEvent')]) + '\n' + \
                     'Users: ' + '\n'
            UserList = self.dataBaseAdapt.getEventUserList(EventWantToChange[consts.eventsColumns.get('idEvent')])
            if (UserList != None):
                if (len(UserList)):
                    for element in UserList:
                        User = self.dataBaseAdapt.getUser(element[consts.groupColumns.get('addres')])
                        if not (User == None):
                            string += User[consts.usersColumns.get('name')] + '  ' + \
                                      User[consts.usersColumns.get('organization')] + '\n'
            string += 'Experts: ' + '\n'
            ExpertList = self.dataBaseAdapt.getEventExpertList(EventWantToChange[consts.eventsUpdateColumns.get('idUnconfirmedUpdate')])
            if (ExpertList != None):
                if (len(ExpertList)):
                    for element in ExpertList:
                        User = self.dataBaseAdapt.getUser(element[consts.groupColumns.get('addres')])
                        if not (User == None):
                            string += User[consts.usersColumns.get('name')] + '  ' + \
                                      User[consts.usersColumns.get('organization')] + '\n'

            self.tb_request_before.setText(string)

    def pb_menu_StartMine_clicked(self):
        if self.CblockChain._MineStat == 0:
            self.CblockChain._MineStat = 1
        else:
            self.CblockChain._MineStat = 0


    def FirstStartLoad(self):
        self.CblockChain.InitAddFunction(self.Load)
        self.cb_request_mode.addItem('"пользователи"')
        self.cb_request_mode.addItem('"мероприятия"')

        self.tw_requestList.horizontalHeader().setStretchLastSection(True)
        self.tw_changeEvent_UserList.horizontalHeader().setStretchLastSection(True)
        self.tw_changeEvent_addedUserList.horizontalHeader().setStretchLastSection(True)
        self.tw_createEvent_UserList.horizontalHeader().setStretchLastSection(True)
        self.tw_eventinfo_userlist.horizontalHeader().setStretchLastSection(True)
        self.tw_lowerRequest_UserList.horizontalHeader().setStretchLastSection(True)
        self.tw_createEvent_addedUserList.horizontalHeader().setStretchLastSection(True)
        self.tw_UsersInfoList.horizontalHeader().setStretchLastSection(True)
        self.Load()
        return True

    def Load(self):
        userList = self.dataBaseAdapt.getUserList()
        self.clearTableWdiget(self.tw_UsersInfoList)
        self.fillUserTableWidget_id_name_organization_isExpert(self.tw_UsersInfoList, userList)

        userInfoList = self.dataBaseAdapt.getUserListByCriterion(1)
        self.clearTableWdiget(self.tw_lowerRequest_UserList)
        self.fillUserTableWidget_id_name_organization(self.tw_lowerRequest_UserList, userInfoList)
        self.cb_registr_choseFileWithPrivateKey.clear()
        self.cb_registr_choseFileWithPrivateKey.addItems(os.listdir('keys'))

        listEvent = []
        self._EventInfoShownListTuple = self.dataBaseAdapt.getEventList()
        for element in self._EventInfoShownListTuple:
            string = str(element[consts.eventsColumns.get('idEvent')]) + "  " + \
                     str(element[consts.eventsColumns.get('name')]) + "  " + \
                     str(element[consts.eventsColumns.get('date')])
            listEvent.append(string)

        self.cb_eventInfo_ChoseEvent.clear()
        self.cb_eventInfo_ChoseEvent.addItems(listEvent)
        self.cb_eventInfo_ChoseEvent_currentIndexChanged()
        self.cb_changeEvent_ChoseEvent.clear()
        self.cb_changeEvent_ChoseEvent.addItems(listEvent)

        listOfAllRequests = []
        RequestList = self.dataBaseAdapt.getRequestList()
        EventUpdateRequestList = self.dataBaseAdapt.getEventUpdateList()
        for element in EventUpdateRequestList:
            string = str(element[consts.eventsUpdateColumns.get('idEvent')]) + "  " + \
                     str(element[consts.eventsUpdateColumns.get('name')]) + "  " + \
                     str(element[consts.eventsUpdateColumns.get('date')])
            listOfAllRequests.append(string)


    def fillUserTableWidget_id_name_organization(self,tableWidget, userInfoList):

        i = 0
        if (len(userInfoList) == 0):
            tableWidget.setRowCount(0)
            return False
        if (userInfoList == None):
            tableWidget.setRowCount(0)
            return False
        tableWidget.setRowCount(len(userInfoList))
        for element in userInfoList:
            tableWidget.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(
                str(element[consts.usersColumns.get('idUser')])))
            tableWidget.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(
                element[consts.usersColumns.get('name')]))
            tableWidget.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(
                element[consts.usersColumns.get('organization')]))
            i += 1
        tableWidget.resizeColumnsToContents()

    def fillUserTableWidget_id_name_organization_isExpert(self,tableWidget, userInfoList):

        i = 0
        if (len(userInfoList) == 0):
            tableWidget.setRowCount(0)
            return False
        if (userInfoList == None):
            tableWidget.setRowCount(0)
            return False
        tableWidget.setRowCount(len(userInfoList))

        tableWidget.setHorizontalHeaderLabels(["Id", "Full Name", "Organization", "Is Expert"])

        for element in userInfoList:
            tableWidget.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(
                str(element[consts.usersColumns.get('idUser')])))
            tableWidget.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(
                element[consts.usersColumns.get('name')]))
            tableWidget.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(
                element[consts.usersColumns.get('organization')]))
            tableWidget.setItem(i, 3, PyQt5.QtWidgets.QTableWidgetItem(
                element[consts.usersColumns.get('isExpert')]))
            i += 1
        tableWidget.resizeColumnsToContents()

    def clearTableWdiget(self, tableWidget):
        tableWidget.setRowCount(0)
        return True

if __name__ == "__main__":
    from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
    app = QApplication(sys.argv)
    ex = GUI_form()



    db = dataBaseAdapter.dataBaseAdapter()
    #db.delEvent(1,1,1,1,1,1,1,1,1,1)
    #db.delRequestDemot(1,1,1)
    #db.delEventUpdate(7,1,1,1,1,1,1,1,1)
    #db.delAccept(6,321)
    db.delAcceptUpdateEvent(1,3,3)

    #ex.setWindowFlags(QtCore.Qt.FramelessWindowHint) # без рамки

    #по центру
    qtRectangle = ex.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    ex.move(qtRectangle.topLeft())
    ex.wdgt_expertMenu.setVisible(False)
    ex.FirstStartLoad()



    ex.show()
    sys.exit(app.exec_())


