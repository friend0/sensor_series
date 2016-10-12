import sys
print(sys.version)

#from zeep import Client
from gritty_soap import Client

address='http://BIW1-BPL010RB1:8081/DA'

print("***********************")
client = Client(wsdl="OpcXMLDaServer.asmx", service_name='OpcXmlDA')
print("Client Created")
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
#print(client.objects.ReadRequestItemList)
print(client.service.Read(Options={'ReturnItemTime':True, 'ReturnItemName':True, 'ReturnErrorText':True, 'ReturnItemName':True}, 
	ItemList={'MaxAge':0, 'Items':{'ItemPath':'', 'ItemName':"RobotVar.TipDressCounter"}}))
