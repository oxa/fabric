import traceback
from horizon import exceptions
from UcsSdk import *

class Vlan:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

def getVlanname(id):
    handle = UcsHandle()
    handle.Login("10.60.6.5","admin","C1sco123")
    vlans = handle.GetManagedObject(None, "fabricVlan")
    for vlandata in vlans:
        if vlandata.Id == str(id):
            vlanname=vlandata.Name
    handle.Logout()
    return vlanname

def getVlans(self):
    handle = UcsHandle()
    handle.Login("10.60.6.5","admin","C1sco123")
    vlanstab=[]
    vlans = handle.GetManagedObject(None, "fabricVlan")
    for vlan in vlans:
        vlanstab.append(Vlan(vlan.Id,vlan.Name,vlan.SwitchId))
    handle.Logout()

    return vlanstab

def addVlan(self, request, context):
    try:
        name = context.get('name')
        id = context.get('id')

        name = str(name)
        id = str(id)

        handle = UcsHandle()
        handle.Login("10.60.6.5","admin","C1sco123")
        obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
        handle.AddManagedObject(obj,"fabricVlan",{"Sharing":"none", "Dn":"fabric/lan/net-"+name+id+"", "Id":""+id+"", "CompressionType":"included", "DefaultNet":"no", "McastPolicyName":"", "PubNwName":"", "Name":""+name+id+"", "PolicyOwner":"local"})


    except:
        print "Exception inside utils.addVlan"
        print traceback.format_exc()
        exceptions.handle(self.request,('Unable to add vlan'))
        return []

# id is required for table
def deleteVlan(self,id):
    try:
        handle = UcsHandle()
        handle.Login("10.60.6.5","admin","C1sco123")
        obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan/net-"+getVlanname(id)})
        handle.RemoveManagedObject(obj)

    except:
        print "Exception inside utils.deleteVlan"
        print traceback.format_exc()
        exceptions.handle(self.request,('Unable to delete vlan'))
        return False