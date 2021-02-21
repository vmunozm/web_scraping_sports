import pymongo
from pymongo import MongoClient
client=MongoClient('localhost')
mydb = client['premier_League_datos']
mycol = mydb['datos']
eq=input("ingrese nombre")
for x in mycol.find(eq):
  print(x)
