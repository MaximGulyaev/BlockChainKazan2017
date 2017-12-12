# -*- coding: utf-8 -*
import dataBaseAdapter
from datetime import datetime, date, time
import consts

dbAdapter = dataBaseAdapter.dataBaseAdapter()
#dbAdapter.getIsExpert('dfsgfdgfdgfdg')
#print(dbAdapter.getUserList()[0][consts.usersColumns.get('organization')])
#print(dbAdapter.getUserListByCriterion(1))
#dbAdapter.getUser('dfsgfdgfdgfdg')
print(dbAdapter.getEventForUser(1,'yMh01IEeNEA1jdBh1wkPIT3boTsaVKAVSL8KI25ti9E'))