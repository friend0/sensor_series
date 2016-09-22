<<<<<<< HEAD
#from PyOPC.OPCContainers import *
#from PyOPC.XDAClient import XDAClient

#def print_options((ilist,options)):
#    print ilist; print options; print

#address = "http://172.16.22.101:8081/DA"
#address = "http://BIW1-BPL010RB1:8081/DA"
#address = "http://BIW1-BPL010RB1:8081/DA"
#xda = XDAClient(OPCServerAddress=address)
#print_options(xda.GetStatus())
#print_options(xda.GetProperties())
#print_options(xda.Read([ItemContainer(ItemName='TipDressCounter')]))


# import osa
#
# cl = osa.Client("OpcXMLDaServer.asmx")
# print cl
# print cl.types
# print cl.service
#
# browse = cl.types.Browse()
# r = cl.types.Read()
# options = cl.types.RequestOptions()
# print browse
# print r
# print options

import sys
print(sys.version)

from gritty_soap import Client

address='http://BIW1-BPL010RB1:8081/DA'

#xda = XDAClient(OPCServerAddress=address,
#                ReturnErrorText=True)
#print(xda)
#print(xda.GetStatus())
#print_options(xda.Browse())
#print_options(xda.Read([ItemContainer(MaxAge=500)],
#                       LocaleID='en-us'))

print("***********************")

client = Client(wsdl="OpcXMLDaServer.asmx", service_name='OpcXmlDA', port_name='BIW1-BPL010RB1')

print("********************")
print (client.service.GetStatus())
print("********************")
print (client.service.GetProperties())
#print("********************")
#print (client.service.SubscriptionPolledRefresh( WaitTime="0", ReturnAllItems="true"))
print("********************")
#print("READ:")
#print(client.service.Read(ItemList={'Items':'KRCReg'}))
print("BROWSE:")
print("********************")
print(client.service.Browse(LocaleID='en-US', ClientRequestHandle="None", BrowseFilter="all",
                            ReturnAllProperties="true", ReturnPropertyValues="true", ReturnErrorText="true"))
print("********************")
print(client.service.Read())

=======
#from PyOPC.OPCContainers import *
#from PyOPC.XDAClient import XDAClient

#def print_options((ilist,options)):
#    print ilist; print options; print

#address = "http://172.16.22.101:8081/DA"
#address = "http://BIW1-BPL010RB1:8081/DA"
#address = "http://BIW1-BPL010RB1:8081/DA"
#xda = XDAClient(OPCServerAddress=address)
#print_options(xda.GetStatus())
#print_options(xda.GetProperties())
#print_options(xda.Read([ItemContainer(ItemName='TipDressCounter')]))


# import osa
#
# cl = osa.Client("OpcXMLDaServer.asmx")
# print cl
# print cl.types
# print cl.service
#
# browse = cl.types.Browse()
# r = cl.types.Read()
# options = cl.types.RequestOptions()
# print browse
# print r
# print options

from pyOPC.gritty_soap import Client
#from PyOPC.OPCContainers import *
#from PyOPC.XDAClient import XDAClient
#import pysimplesoap
#import soap2py

address='http://BIW1-BPL010RB1:8081/DA'

#xda = XDAClient(OPCServerAddress=address,
#                ReturnErrorText=True)
#print(xda)
#print(xda.GetStatus())
#print_options(xda.Browse())
#print_options(xda.Read([ItemContainer(MaxAge=500)],
#                       LocaleID='en-us'))

print("***********************")

client = Client(wsdl="OpcXMLDaServer.asmx", service_name='OpcXmlDA', port_name='BIW1-BPL010RB1')

print("********************")
print (client.service.GetStatus())
print("********************")
print (client.service.GetProperties())
#print("********************")
#print (client.service.SubscriptionPolledRefresh( WaitTime="0", ReturnAllItems="true"))
print("********************")
#print("READ:")
#print(client.service.Read(ItemList={'Items':'KRCReg'}))
print("BROWSE:")
print("********************")
print(client.service.Browse(LocaleID='en-US', ClientRequestHandle="None", BrowseFilter="all",
                            ReturnAllProperties="true", ReturnPropertyValues="true", ReturnErrorText="true"))
print("********************")
print(client.service.Read())

>>>>>>> 0dd844b72326a5dc6c7b568bbf0813a6c6122aec
