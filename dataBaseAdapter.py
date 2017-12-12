import sqlite3
import consts
import json
import helper
from datetime import datetime, date, time

class dataBaseAdapter:
    def __init__(self):
        creationTableResult = self.rollOut()
        print(creationTableResult)

    def rollOut(self):
        conn = sqlite3.connect('resourse/db.sqlite')
        cursor = conn.cursor()
        try:
            cursor.execute(consts.createTableUsers)
            cursor.execute(consts.createTableEvent)
            cursor.execute(consts.createTableEventUpdate)
            cursor.execute(consts.createTableGroups)
            cursor.execute(consts.createTableRequest)
            cursor.execute(consts.createTableTransactionInBlock)
            cursor.execute(consts.createTableUnconfirmedTransaction)
            cursor.execute(consts.createTableBlock)
            cursor.execute(consts.createTableAddres)
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulCreation
        except sqlite3.OperationalError as error:
            return error

    def addUser(self,addres, Name, birthDay, isExpert, publicKey, organization):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (addres,name,birthday,isExpert,openKey,organization) "
                           "VALUES (?,?,?,?,?,?)"
                           ,(addres, Name, birthDay, isExpert, publicKey, organization))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        #except:
        #    return None

    def getIsExpert(self, addr):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE addres = ('%s')" % (addr))
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return row[4]
        except:
            return None

    def getUserListByCriterion(self, isExpert):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE isExpert = ('%s')" % (isExpert))
            rows = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def getUserPublicKey(self, addr):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE addres = ('%s')" % (addr))
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return row[5]
        except:
            return None

    def getUserList(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ")
            rows = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def setExpert(self, addr):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET isExpert = 1 WHERE addres = ('%s')" % (addr))
            cursor.execute("SELECT * FROM users WHERE addres = ('%s')" % (addr))
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return 'name : {0}({1}) rise to expert'.format(row[2], row[0])
        #except:
        #    return None

    def setStudent(self, addr):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET isExpert = 0 WHERE addres = ('%s')" % (addr))
            cursor.execute("SELECT * FROM users WHERE addres = ('%s')" % (addr))
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return 'name : {0}({1}) rise to expert'.format(row[2], row[0])
        except:
            return None

    def getUser(self, addr):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE addres = ('%s')" % (addr))
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            return row
        except:
            return None

    def addUserToGroup(self, addres, idGroup, typeGroup):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO groups (idGroup,addres) "
                           "VALUES ('%s','%s','%s')"
                           % (idGroup, addres, typeGroup))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        except:
            return None

    def deleteUserOutGroup(self, addres, idGroup):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM groups WHERE addres = ('%s') and usersGroup = ('%s')" % (addres,idGroup))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        except:
            return None

    def getUsersInGroup(self, idGroup):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE idGroup = ('%s')" % (idGroup))
            rows = cursor.fetchall()
            # res = helper.tupleUserToDict(row)
            conn.commit()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def addEvent(self, creator, name, date, data, competence, rating, numOfExperts, expertsList, usersList,timestamp):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE addres = ('%s')" % (creator))
            row = cursor.fetchone()
            creator = row[consts.usersColumns.get('addres')]
            cursor.execute("SELECT MAX(idGroup) FROM groups")
            currentLastNumberRow = cursor.fetchone()[0]
            if (currentLastNumberRow == None):
                currentLastNumberRow = 0
            idExpertsGroup = currentLastNumberRow + 1
            idUsersGroup = idExpertsGroup + 1
            cursor.execute(
                "INSERT INTO event (creator,name,date,data,competence,raiting,numOfExperts,idExpertsGroup,idUsersGroup,version,currentUpdateIndex,timestamp) "
                "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
                % (creator, name, date, data, competence, rating, numOfExperts, idExpertsGroup, idUsersGroup, 0, 0, timestamp))
            for user in usersList:
                cursor.execute("INSERT INTO groups (usersGroup,addres,typeGroup) "
                               "VALUES ('%s','%s','%s')"
                               % (idUsersGroup, user[consts.usersColumns.get('addres')], 0))
            for expert in expertsList:
                cursor.execute("INSERT INTO groups (usersGroup,addres,typeGroup) "
                               "VALUES ('%s','%s','%s')"
                               % (idExpertsGroup, expert[consts.usersColumns.get('addres')], 1))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        except :
            return None

    def getEventUserList(self, eventId):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM groups WHERE usersGroup = "
                           "(SELECT idUsersGroup FROM event WHERE idEvent = ('%s'))" % (eventId))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except :
            return None

    def getEventExpertList(self, eventId):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM groups WHERE usersGroup = "
                           "(SELECT idExpertsGroup FROM event WHERE idEvent = ('%s'))" % (eventId))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except :
            return None

    def incCurrentUpdateIndex(self, eventId):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("UPDATE event SET currentUpdateIndex = currentUpdateIndex + 1 "
                           "WHERE idEvent = ('%s')" % (eventId))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        except:
            return None

    def getEvent(self, eventId):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM event WHERE idEvent = ('%s')" % (eventId))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row
        except :
            return None

    def getEventList(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM event")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except :
            return None

    def changeEvent(self, id, name,data, date, competence, rating, numOfExperts, expertslist, userslist):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            if (expertslist != None):

                cursor.execute("SELECT idExpertsGroup FROM event WHERE idEvent = ('%s')"% (id))
                rowNumber = cursor.fetchone()[0]
                cursor.execute("DELETE FROM groups WHERE usersGroup = ('%s')" % (rowNumber))
                for expert in expertslist:
                    cursor.execute("INSERT INTO groups (usersGroup,addres,typeGroup) "
                                   "VALUES ('%s','%s','%s')"
                                   % (rowNumber, expert[consts.usersColumns.get('addres')], 1))

            if (userslist != None):

                cursor.execute("SELECT idUsersGroup FROM event WHERE idEvent = ('%s')"% (id))
                rowNumber = cursor.fetchone()[0]
                cursor.execute("DELETE FROM groups WHERE usersGroup = ('%s')" % (rowNumber))
                for user in userslist:
                    cursor.execute("INSERT INTO groups (usersGroup,addres,typeGroup) "
                                   "VALUES ('%s','%s','%s')"
                                   % (rowNumber, user[consts.usersColumns.get('addres')], 0))

            if (name != None):
                cursor.execute("UPDATE event SET name = ('%s') WHERE idEvent = ('%s')" % (name,id))

            if (data != None):
                cursor.execute("UPDATE event SET data = ('%s') WHERE idEvent = ('%s')" % (data, id))

            if (date != None):
                cursor.execute("UPDATE event SET date = ('%s') WHERE idEvent = ('%s')" % (data, id))

            if (competence != None):
                cursor.execute("UPDATE event SET competence = ('%s') WHERE idEvent = ('%s')" % (competence, id))

            if (rating != None):
                cursor.execute("UPDATE event SET raiting = ('%s') WHERE idEvent = ('%s')" % (rating, id))

            if (numOfExperts != None):
                cursor.execute("UPDATE event SET numOfExperts = ('%s') WHERE idEvent = ('%s')" % (numOfExperts, id))

            cursor.execute("UPDATE event SET version = event.version + 1 "
                           "WHERE idEvent = ('%s')" % (id))

            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        except:
            return None

    def getUsersEventList(self,addr, isExpert):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT usersGroup FROM groups WHERE addres = (?) AND typeGroup = (?)", (addr, isExpert))
            rows = cursor.fetchall()
            list = []
            for row in rows:
                cursor.execute("SELECT * FROM event "
                               "WHERE idUsersGroup = ('%s') OR idExpertsGroup = ('%s')" % (row[0], row[0]))
                list.append(cursor.fetchone())
            cursor.close()
            conn.close()
            return list
        except:
            return None


    def addRequestDemot(self,addrFrom, addrTo, Createtime):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(idGroup) FROM groups")
            idExpertGroup = cursor.fetchone()[0] + 1
            cursor.execute("INSERT INTO request (addresFrom,addresTo,idConfirmExpertGroup,typeRequest,quantityAccepted,date) "
                           "VALUES (?,?,?,?,?,?)"
                            ,(addrFrom, addrTo, idExpertGroup,1,1,Createtime))
            cursor.execute("INSERT INTO groups (addres,usersGroup,typeGroup,accept) "
                           "VALUES (?,?,?,?)"
                           ,(addrFrom,idExpertGroup,1,1))

            conn.commit()
            cursor.close()
            conn.close()
            return idExpertGroup
        #except:
        #    return None


    def addRequestRise(self,addrFrom, CreateTime):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(idGroup) FROM groups")
            idExpertGroup = cursor.fetchone()[0]
            if idExpertGroup == None:
                idExpertGroup = 0
            idExpertGroup += 1
            cursor.execute("INSERT INTO request (addresFrom,addresTo,idConfirmExpertGroup,typeRequest,quantityAccepted,date) "
                           "VALUES (?,?,?,?,?,?)",
                           (addrFrom, addrFrom, idExpertGroup,0,0, CreateTime))#todo kek
            cursor.execute("INSERT INTO groups (addres,usersGroup,typeGroup,accept) "
                           "VALUES (?,?,?,?)",
                           (addrFrom, idExpertGroup, 1, 1))
            conn.commit()
            cursor.close()
            conn.close()
            return idExpertGroup
        #except:
         #   return None

    def getRequestList(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM request")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def getRequestByToAddrAndType(self,addr,type):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM request "
                           "WHERE addresTo = ('%s') and typeRequest = ('%s')"
                           %(addr,type))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def getRequestById(self, idRequest):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM request "
                           "WHERE idRequest = (?)",
                           (idRequest,))
            rows = cursor.fetchone()
            cursor.close()
            conn.close()
            return rows
        #except:
        #   return None

    def addAccept(self,id, addrExp):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT idConfirmExpertGroup FROM request "
                           "WHERE idRequest = ('%s')"% (id))
            idExpGroup = cursor.fetchone()[0]
            cursor.execute ("SELECT Count(*) from groups "
                            "WHERE addres = ('%s') and usersGroup = ('%s')"
                            %(addrExp,idExpGroup))
            if (cursor.fetchone()[0] == 1):
                cursor.execute("UPDATE groups SET accept = 1 "
                           "WHERE usersGroup = ('%s') and addres = ('%s')" % (idExpGroup, addrExp))
            else:
                cursor.execute("INSERT INTO groups (usersGroup,addres,typeGroup,accept) "
                               "VALUES (?,?,?,?)",
                               (idExpGroup,addrExp,1,1))


            cursor.execute("SELECT Count(*) from groups "
                           "WHERE usersGroup = ('%s')"
                           %(idExpGroup))
            countExp = cursor.fetchone()[0]
            cursor.execute("UPDATE request SET quantityAccepted = ('%s')"
                           "WHERE idRequest = ('%s')" % (countExp, id))
            conn.commit()
            cursor.close()
            conn.close()
            return countExp
        #except:
        #    return None

    def addUncTransaction(self, address, type, data, publicKey, signature):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO unconfirmedTransaction (address,type,data,openKey,signature)"
                           "VALUES (?,?,?,?,?)"
                           ,(address,type,data,publicKey, signature))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        #except:
        #    return None

    def getCountOfUncTransaction(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM unconfirmedTransaction")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        except:
            return None

    def getUncTransactionList(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM unconfirmedTransaction")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def deleteUncTransaction(self,id):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unconfirmedTransaction "
                           "WHERE idTransaction = ('%s')" %(id))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        except:
            return None

    def addEventUpdate(self, id, name,data, date, competence, numOfExperts, expertsList, usersList, timestamp):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT version,currentUpdateIndex FROM event "
                           "WHERE idEvent = (?)", (id,))
            m = cursor.fetchone()
            version = m[0]
            currentUpdateIndex = m[1]
            cursor.execute("SELECT MAX(updateIndex) FROM eventUpdate "
                           "WHERE idEvent = (?) and version =(?)", (id,version))
            updateIndex = cursor.fetchone()[0]

            cursor.execute("SELECT MAX(idGroup) FROM groups")
            idExpertsGroup = cursor.fetchone()[0] + 1
            idUsersGroup = idExpertsGroup + 1

            for user in usersList:
                cursor.execute("INSERT INTO groups (usersGroup,addres,typeGroup) "
                               "VALUES (?,?,?)",
                                (idUsersGroup, user[consts.usersColumns.get('addres')], 0))
            for expert in expertsList:
                cursor.execute("INSERT INTO groups (usersGroup,addres,typeGroup) "
                               "VALUES (?,?,?)",
                               (idExpertsGroup, expert[consts.usersColumns.get('addres')], 1))

            if (updateIndex == None):
                updateIndex = currentUpdateIndex + 1
            else:
                updateIndex += 1
            cursor.execute("INSERT INTO eventUpdate "
                           "(idEvent,name,data,date,competence,numOfExperts,idExpertsGroup,idUsersGroup,updateIndex,timestamp,version) "
                           "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                           (id, name,data, date, competence, numOfExperts, idExpertsGroup, idUsersGroup,updateIndex,timestamp,version))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser

        #except:
        #    return None

    def getEventUpdateUserList(self, eventId):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM groups WHERE usersGroup = "
                           "(SELECT idUsersGroup FROM eventUpdate WHERE idUnconfirmedUpdate = ('%s'))" % (eventId))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except :
            return None

    def getEventUpdateExpertList(self, eventId):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM groups WHERE usersGroup = "
                           "(SELECT idExpertsGroup FROM eventUpdate WHERE idUnconfirmedUpdate = ('%s'))" % (eventId))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except :
            return None

    def getEventUpdateList(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM eventUpdate")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def getEventUpdate(self,id, UpdateIndex):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM eventUpdate "
                           "WHERE idEvent = ('%s') AND updateIndex = ('%s')"
                           %(id, UpdateIndex))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def addAcceptUpdateEvent(self, id, UpdateIndex, addr):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT idExpertsGroup FROM eventUpdate "
                           "WHERE idEvent = ('%s') AND updateIndex = ('%s')"
                           % (id, UpdateIndex))
            groupId = cursor.fetchone()[0]
            cursor.execute("UPDATE groups SET accept = ('%s')"
                           "WHERE usersGroup = ('%s') and addres = ('%s')" % (1, groupId, addr))

            cursor.execute("SELECT COUNT(*) FROM groups "
                           "WHERE usersGroup = ('%s') and accept = 1 "
                           %(groupId) )
            countAgreement = cursor.fetchone()[0]
            cursor.execute("UPDATE eventUpdate SET numOfExperts = ('%s') "
                           "WHERE usersGroup = ('%s') and idEvent = ('%s')"
                           % (countAgreement, groupId, id))
            conn.commit()
            cursor.close()
            conn.close()
            return countAgreement
        except:
            return None

    def getUserById(self,userID):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users "
                           "WHERE idUser = ('%s') "% (userID))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row
        except:
            return None

    def addAddres(self,addres):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO addres (addres) VALUES ('%s')"%(addres))
            conn.commit()
            cursor.close()
            conn.close()
        except:
            return None

    def getLastBlock(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Block ")
            countRows = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM Block "
                           "WHERE idBlock = ('%s')"
                           %(countRows))
            lastBlock = cursor.fetchone()
            cursor.close()
            conn.close()
            return lastBlock
        except:
            return 0

    def getPrevBlockHash(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Block ")
            countRowsMinusOne = cursor.fetchone()[0]
            cursor.execute("SELECT hash FROM Block "
                           "WHERE idBlock = ('%s')"
                           %(countRowsMinusOne))
            prevBlock = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return prevBlock
        except:
            return 0

    def getBlockByHash(self,hash):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Block "
                           "WHERE hash = ('%s')"
                           %(hash))
            curBlock = cursor.fetchone()
            cursor.close()
            conn.close()
            return curBlock
        except:
            return None


    def addBlock(self,hash,timestamp,count,complexity,nonce):
        prevBlockHash = self.getPrevBlockHash()
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Block (idPrevBlockHash, hash, timestamp, count, complexity, nonce) "
                           "VALUES ('%s','%s','%s','%s','%s','%s')"
                           % (prevBlockHash,hash,timestamp,count,complexity,nonce))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        except:
            return None

    def getHashChain(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM Block ")
            curHashChain = cursor.fetchall()
            cursor.close()
            conn.close()
            return curHashChain
        except:
            return None

    def addTransaction(self, address, type, data, publicKey, signature, idBlock):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactionInBlock (address,type,data,openKey,signature,idBlock)"
                           "VALUES (?,?,?,?,?,?)"
                           ,(address,type,data,publicKey, signature,idBlock))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        #except:
        #    return None

    def getCountOfTransaction(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactionInBlock")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        except:
            return None

    def getTransactionList(self):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactionInBlock")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        except:
            return None

    def deleteTransaction(self,id):
        try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactionInBlock "
                           "WHERE idTransaction = ('%s')" %(id))
            conn.commit()
            cursor.close()
            conn.close()
            return consts.successfulAddNewUser
        except:
            return None

    def getTransactByIdBlock(self, idBlock):
        #try:
            conn = sqlite3.connect('resourse/db.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactionInBlock"
                           "WHERE idBlock = (?)", (idBlock,))
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        #except:
         #   return None