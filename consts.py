import sqlite3



userNotExist = "Attention. User not exist"
userLogoutAtt = "Attention. You are logout"
createUserAtt = "Attention. You sent a registration request. Please wait while one of the registered users system will not confirm your registration."
errorInPath = "Attention. Error in file path"
errorSomethingWentWrong = "Error Something went wrong"
erorLoginToNet = "Please login to net"
addUser = "User added"
notAddUser = "User not added"
userNotExpert = "Error. User isn't expert"
errorNotPermission = "Not permission for you"
isYetUsersAdd = 'Yet add user?Y/n'
isYetUserErase = 'Yet erase user?Y/n'

usersColumns = {
    'idUser' : 0,
    'addres' : 1,
    'name' : 2,
    'birthday' : 3,
    'isExpert' : 4,
    'publicKey' : 5,
    'organization' : 6
}


typeNetQuery = {
    'transaction' : 1,
    'block' : 2,
    'length' : 3,
    'fullChain' : 4,
    'isEqChain' : 5,
    'eqChain' : 51,
    'notEqChain' : 52,
    'addUser' : 6,
    'error' : 7,
    'SendHashChain': 8,
    'SendBlockList': 9,
    'ShowMeNet': 10,
}

eventsColumns = {
    'idEvent':0,
    'creator':1,
    'name':2,
    'date':3,
    'competence':4,
    'raiting':5,
    'data':6,
    'numOfExperts':7,
    'idExpertsGroup':8,
    'idUsersGroup':9,
    'version':10,
    'currentUpdateIndex':11,
    'timestamp': 12,
}

groupColumns = {
    'idGroup': 0,
    'addres': 1,
    'usersGroup': 2,
    'typeGroup': 3,
}

requestColumns = {
  'idRequest': 0,
  'addresFrom': 1,
  'addresTo': 2,
  'idConfirmExpertGroup': 3,
  'typeRequest': 4,
  'quantityAccepted': 5,
  'date': 6,

}

eventsUpdateColumns = {
  'idUnconfirmedUpdate': 0,
  'idEvent': 1,
  'name': 2,
  'data': 3,
  'date': 4,
  'competence': 5,
  'numOfExperts': 6,
  'idExpertsGroup': 7,
  'idUsersGroup': 8,
  'updateIndex': 9,
  'timestamp': 10,
  'idConfirmExpertGroup': 11,
  'version': 12,
}

transaction = {
    'idTransaction': 0,
    'type': 2,
    'data': 3,
    'publicKey': 4,
    'hash': 5,
    'signature': 6,
    'address': 7,
    'idBlock': 1
}

BlockColumns = {
    'idBlock':0,
    'PrevBlockHash':1,
    'hash':2,
    'timestamp':3,
    'count':4,
    'complexity':5,
    'nonce':6,
}

successfulCreation = "Tables created"
successfulAddNewUser = "User created"

createTableUsers = '''
CREATE TABLE users (
  idUser INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  addres VARCHAR,
  name VARCHAR,
  birthday VARCHAR,
  isExpert INT,
  openKey VARCHAR,
  organization VARCHAR
)
'''

createTableAddres = '''
CREATE TABLE addres (
	idAddres	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	addres	INTEGER UNIQUE
)
'''

createTableGroups = '''
CREATE TABLE groups (
  idGroup INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  addres VARCHAR,
  usersGroup INTEGER,
  typeGroup INTEGER,
  accept INTEGER
)
'''

createTableRequest = '''
CREATE TABLE request (
  idRequest INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  addresFrom VARCHAR,
  addresTo VARCHAR,
  idConfirmExpertGroup INT,
  typeRequest INT,
  quantityAccepted INT,
  date INT
)
'''

createTableUnconfirmedTransaction = '''
CREATE TABLE unconfirmedTransaction (
  idTransaction INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  type INT,
  data VARCHAR,
  openKey VARCHAR,
  hash VARCHAR,
  signature VARCHAR,
  address VARCHAR
)
'''

createTableTransactionInBlock = '''
CREATE TABLE transactionInBlock (
  idTransaction INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  idBlock INT,
  type INT,
  data VARCHAR,
  openKey VARCHAR,
  hash VARCHAR,
  signature VARCHAR,
  address VARCHAR
)
'''

createTableEvent = '''
CREATE TABLE event (
  idEvent INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  creator INT,
  name VARCHAR,
  date datetime,
  competence INT,
  raiting INT,
  data VARCHAR,
  numOfExperts INT,
  idExpertsGroup INT,
  idUsersGroup INT,
  version INT,
  currentUpdateIndex INT,
  timestamp INT
)
'''

createTableEventUpdate = '''
CREATE TABLE eventUpdate (
  idUpdateEvent INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  idEvent INTEGER NOT NULL,
  name VARCHAR,
  data VARCHAR,
  date datetime,
  competence INT,
  numOfExperts INT,
  idExpertsGroup INT,
  idUsersGroup INT,
  updateIndex INT,
  timestamp datetime,
  confirmRemain INT,
  idConfirmExpertGroup INTEGER ,
  version INTEGER
)
'''

createTableBlock = '''
CREATE TABLE Block(
  idBlock INTEGER PRIMARY KEY NOT NULL,
  idPrevBlockHash INT,
  hash VARCHAR,
  timestamp datetime,
  count INT,
  complexity INT,
  nonce datetime
)
'''

