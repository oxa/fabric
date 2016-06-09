from UcsSdk import *


handle = UcsHandle()
handle.Login("10.60.6.5","admin","C1sco123")
vlans = handle.GetManagedObject(None, "fabricVlan")
for vlandata in vlans:
    if vlandata.Id == "17":
        vlanname=vlandata.Name
handle.Logout()
print vlanname