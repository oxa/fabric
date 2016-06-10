import re

def UcsCreateVlan():
    specific = "13,14,18-21"
    chn = specific.split(",")
    single_vlan = r"^[0-9]*$"
    range_vlan= r"^[0-9]{1,4}[-][0-9]{1,4}$"
    for value in chn:
        if re.search(single_vlan, value) is not None:
            print "This is a vlan : "+value
        if re.search(range_vlan, value) is not None:
            stri=value.split("-")
            if stri[0] < stri[1] :
                for i in range (int(stri[0]), int(stri[1])+1):
                    print "this is also a vlan : "+str(i)

if __name__ == "__main__":
    UcsCreateVlan()