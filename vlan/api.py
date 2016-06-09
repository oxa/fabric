import sys, time
#import requests
sys.path.append('/usr/local/lib/python2.7/dist-packages')

from functools import wraps
from UcsSdk import *
from UcsSdk.MoMeta.VnicEtherIf import VnicEtherIf
from flask import Flask, render_template, request,make_response,current_app, redirect
from datetime import timedelta
from functools import update_wrapper
import collections
import re
import sys
from flask import Flask, jsonify
#import flask_cors

app = Flask(__name__)

#app.config['CORS_HEADERS'] = 'Content-Type'
#cors = flask_cors.CORS(app, resources={r"/.api/ucs/*": {"origins": "*"}},allow_headers='Content-Type')

def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('vlanCall', False)
        if callback:
            content = str(callback) + '(' + str(f().data) + ')'
            return current_app.response_class(content, mimetype='application/json')
        else:
            return f(*args, **kwargs)
    return decorated_function

UcSdk.register("")

def crossdomain(origin=None, methods=None, headers=None,max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

@app.route('/.api/ucs/remove-vlan', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def UcsRemoveVlan():
    AnswerSingle = []

    try:
        ip_address = request.args.get('ip_address',type=str)
        login = request.args.get('login',type=str)
        password = request.args.get('password', type=str)
        radical = request.args.get('radical', type=str)
        specific = request.args.get('specific',type=str)
        group = request.args.get('group', type=str)

        org = request.args.get('org', type=str)
        template = request.args.get('template', type=str)
        vmnic = request.args.get('vmnic',type=str)

        #Login to UCS Manager
        handle = UcsHandle()
        handle.Login(ip_address, login, password)

        chn = convert(specific.split(","))
        print chn
        pattern = r"^[0-9]*$"
        patternR = r"^[0-9]{1,4}[-][0-9]{1,4}$"


        for value in chn:
            if re.search(pattern, value) is not None:

                # Detach Vlan from template
                if org != "None" and template != "None" and vmnic != "None" and radical != None :
                    try :
                        handle.StartTransaction()
                        obj = handle.GetManagedObject(None, None, {"Dn":"org-"+org+"/ls-"+template+"/ether-"+vmnic+"/if-"+radical+value+""})
                        mo= handle.RemoveManagedObject(obj)
                        handle.CompleteTransaction()
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+value+" detached to "+template+" on "+vmnic+" to UCSM "+ip_address+".")
                    except Exception, err:
                        print str(err)
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+value+" not found from "+template+" on UCSM "+ip_address+".")

                 # Detach Vlan from group
                if group != "None" :
                    try :
                        handle.StartTransaction()
                        obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
                        mo = handle.AddManagedObject(obj, "fabricNetGroup", {"NativeNet":"", "PolicyOwner":"local", "Dn":"fabric/lan/net-group-"+group+"", "Descr":"", "Type":"mgmt"}, True)
                        obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan/net-group-"+group+"/net-"+radical+value+""})
                        mo_1 = handle.RemoveManagedObject(obj)
                        handle.CompleteTransaction()
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+value+" detached to "+group+" on UCSM "+ip_address+".")
                    except Exception, err:
                        print str(err)
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+value+" not found from "+group+" on UCSM "+ip_address+".")

                #Delete Vlan
                try :
                    obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan/net-"+radical+value+""})
                    handle.RemoveManagedObject(obj)
                    AnswerSingle.insert(len(AnswerSingle),"Vlan "+radical+value+" removed.")
                except Exception, err:
                    print str(err)
                    AnswerSingle.insert(len(AnswerSingle),"Vlan "+radical+value+" not found.")

            if re.search(patternR, value) is not None:
                stri=value.split("-")
                if stri[0] < stri[1] :
                    cpt=int(stri[1])-int(stri[0])

                    for i in range (0, cpt+1) :
                        res=int(stri[0])+i
                        resST=str(res)


                        #Detach Vlan from template
                        if org != "None" and template != "None" and vmnic != "None" and radical != None :
                            try :
                                handle.StartTransaction()
                                obj = handle.GetManagedObject(None, None, {"Dn":"org-"+org+"/ls-"+template+"/ether-"+vmnic+"/if-"+radical+resST+""})
                                mo= handle.RemoveManagedObject(obj)
                                handle.CompleteTransaction()
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+resST+" detached to "+template+" on "+vmnic+" to UCSM "+ip_address+".")
                            except Exception, err:
                                print str(err)
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+resST+" not found from "+template+" on UCSM "+ip_address+".")

                        #Detach Vlan from group
                        if group != "None" :
                            try :
                                handle.StartTransaction()
                                obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
                                mo = handle.AddManagedObject(obj, "fabricNetGroup", {"NativeNet":"", "PolicyOwner":"local", "Dn":"fabric/lan/net-group-"+group+"", "Descr":"", "Type":"mgmt"}, True)
                                obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan/net-group-"+group+"/net-"+radical+resST+""})
                                mo_1 = handle.RemoveManagedObject(obj)
                                handle.CompleteTransaction()
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+resST+" detached to "+group+" on UCSM "+ip_address+".")
                            except Exception, err:
                                print str(err)
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+resST+" not found from "+group+" on UCSM "+ip_address+".")

                        #Delete Vlan
                        try :
                            obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan/net-"+radical+resST+""})
                            handle.RemoveManagedObject(obj)
                            AnswerSingle.insert(len(AnswerSingle),"Vlan "+radical+resST+" removed.")
                        except Exception, err :
                            print str(err)
                            AnswerSingle.insert(len(AnswerSingle),"Vlan "+radical+resST+" not found.")


        handle.Logout()
        return jsonify(resultat=AnswerSingle)
       #return 0
    except Exception, err:
        print "Exception : ",str(err)
        import traceback, sys
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        return jsonify(return_code="Failed", traceback=traceback.print_exc(file=sys.stdout), LogError="Exception : "+str(err),details="Vlan(s) " + specific + " cannot removed.")




@app.route('/.api/ucs/create-vlan', methods=['GET'])
@support_jsonp
def UcsCreateVlan():
    AnswerSingle = []
    try:
        ip_address = request.args.get('ip_address',type=str)
        login = request.args.get('login',type=str)
        password = request.args.get('password', type=str)
        radical = request.args.get('radical', type=str)
        specific = request.args.get('specific',type=str)
        group = request.args.get('group', type=str)

        org = request.args.get('org', type=str)
        template = request.args.get('template', type=str)
        vmnic = request.args.get('vmnic',type=str)

        #Login to UCS Manager
        handle = UcsHandle()
        handle.Login(ip_address, login, password)

        chn = convert(specific.split(","))
        #print chn
        pattern = r"^[0-9]*$"
        patternR = r"^[0-9]{1,4}[-][0-9]{1,4}$"
        for value in chn:
            if re.search(pattern, value) is not None:

                #Create Vlan
                if radical != None :
                    try :
                        obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
                        handle.AddManagedObject(obj,"fabricVlan",{"Sharing":"none", "Dn":"fabric/lan/net-"+radical+value+"", "Id":""+value+"", "CompressionType":"included", "DefaultNet":"no", "McastPolicyName":"", "PubNwName":"", "Name":""+radical+value+"", "PolicyOwner":"local"})
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+radical+value+" created.")
                    except Exception, err:
                        print str(err)
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+radical+value+" already exist.")

                # Attach vlan
                if group != "None" and radical != None :
                    try :
                        handle.StartTransaction()
                        obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
                        mo = handle.AddManagedObject(obj, "fabricNetGroup", {"NativeNet":"", "PolicyOwner":"local", "Dn":"fabric/lan/net-group-"+group+"", "Descr":"", "Type":"mgmt"}, True)
                        mo_1 = handle.AddManagedObject(mo, "fabricPooledVlan", {"Name":""+radical+value+"", "Dn":"fabric/lan/net-group-"+group+"/net-"+radical+value+""}, True)
                        handle.CompleteTransaction()
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+value+" attached to "+group+" on UCSM "+ip_address+".")
                    except Exception, err:

                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+value+" already exist from "+group+" on UCSM "+ip_address+".")

                #Attach template
                if org != "None" and template != "None" and vmnic != "None" and radical != None :
                    try :
                        handle.StartTransaction()
                        obj = handle.GetManagedObject(None, None, {"Dn":"org-"+org+"/ls-"+template+"/ether-"+vmnic+""})
                        mo = handle.AddManagedObject(obj, VnicEtherIf.ClassId(), {VnicEtherIf.NAME: ""+radical+value+"", VnicEtherIf.VNET: ""+value+""})
                        handle.CompleteTransaction()
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+value+" attached to "+template+" on "+vmnic+" to UCSM "+ip_address+".")
                    except Exception, err :
                        AnswerSingle.insert(len(AnswerSingle),"Vlan "+value+" already exist from "+template+" on UCSM "+ip_address+".")

            if re.search(patternR, value) is not None:
                stri=value.split("-")
                if stri[0] < stri[1] :
                    cpt=int(stri[1])-int(stri[0])

                    for i in range (0, cpt+1) :
                        res=int(stri[0])+i
                        resST=str(res)

                        #Create Vlan
                        if radical != None :
                            try :
                                obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
                                handle.AddManagedObject(obj,"fabricVlan",{"Sharing":"none", "Dn":"fabric/lan/net-"+radical+resST+"", "Id":""+resST+"", "CompressionType":"included", "DefaultNet":"no", "McastPolicyName":"", "PubNwName":"", "Name":""+radical+resST+"", "PolicyOwner":"local"})
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+radical+resST+" created.")
                            except:
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+radical+resST+" already exist.")

                        #Attach vlans
                        if group != "None" and radical != None :
                            try :
                                handle.StartTransaction()
                                obj = handle.GetManagedObject(None, None, {"Dn":"fabric/lan"})
                                mo = handle.AddManagedObject(obj, "fabricNetGroup", {"NativeNet":"", "PolicyOwner":"local", "Dn":"fabric/lan/net-group-"+group+"", "Descr":"", "Type":"mgmt"}, True)
                                mo_1 = handle.AddManagedObject(mo, "fabricPooledVlan", {"Name":""+radical+resST+"", "Dn":"fabric/lan/net-group-"+group+"/net-"+radical+resST+""}, True)
                                handle.CompleteTransaction()
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+resST+" attached to "+group+" on UCSM "+ip_address+".")
                            except Exception, err:
                                print str(err)
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+resST+" already exist from "+group+" on UCSM "+ip_address+".")

                        #Attach template
                        if org != "None" and template != "None" and vmnic != "None" and radical != None :
                            try :
                                handle.StartTransaction()
                                obj = handle.GetManagedObject(None, None, {"Dn":"org-"+org+"/ls-"+template+"/ether-"+vmnic+""})
                                mo = handle.AddManagedObject(obj, VnicEtherIf.ClassId(), {VnicEtherIf.NAME: ""+radical+resST+"", VnicEtherIf.VNET: ""+resST+""})
                                handle.CompleteTransaction()
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+resST+" attached to "+template+" on "+vmnic+" to UCSM "+ip_address+".")
                            except Exception, err:
                                print str(err)
                                AnswerSingle.insert(len(AnswerSingle),"Vlan "+resST+" already exist. from "+template+" on UCSM "+ip_address+".")


        handle.Logout()
        #return jsonify(resultat=AnswerSingle)
        return AnswerSingle
    except Exception, err:
        print "Exception : ",str(err)
        import traceback, sys
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        #return jsonify(return_code="Failed", traceback=traceback.print_exc(file=sys.stdout), LogError="Exception : "+str(err),details="Vlan(s) " + specific + " cannot created.")

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)
