import requests
import re
import json

netbox_link = 'http://192.168.0.201:8000'
prtg_link = 'https://192.168.0.254'
username_prtg = 'prtgadmin'
password_prtg = 'Prtglab2022'

#APIs
url_netbox = netbox_link+"/api/dcim/devices/?tag=prtg"
headers_netbox = {
    'Accept': 'application/json',
    'Authorization': 'Token 0123456789abcdef0123456789abcdef01234567'
    }
url_prtg = prtg_link+"/api/table.json?content=devices&columns=objid,probe,group,device,status,host&count=*&username=prtgadmin&password=Prtglab2022"

#TARGET GROUPS IN PRTG
prtg_network_group_id = 2040
prtg_group_server_id = 2041

#TEMPLATES IN PRTG
prtg_network_device_id = 2043
prtg_server_device_id = 2045

def api_request(url,headers=None,payload=None):
    try:
        response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    except requests.exceptions.SSLError:
        pass
    jsonResponse = response.json()
    return jsonResponse

def create_new_object_prtg(url):
    try:
        response = requests.request("GET", url,verify=False)

    except requests.exceptions.SSLError:
        pass
def resumeobj(resumeurl):
    try:
        resume_device = requests.request("GET", resumeurl,verify=False)

    except requests.exceptions.SSLError:
        pass

list_device_add = []


netbox_get_devices = api_request(url=url_netbox,headers=headers_netbox)
prtg_get_devices = api_request(url=url_prtg)



#GET DEVICE INFORMATION FROM NETBOX
n = 0
list_netbox_devices = []
for dictionary in netbox_get_devices['results']:
    n+=1
    netbox_device_name = dictionary['name']
    netbox_device_role = dictionary['device_role']['display']
    netbox_device_ip = dictionary['primary_ip']['display']
    netbox_device_status = dictionary['status']['value']
    list_netbox_devices.append({netbox_device_name:{'device_role':netbox_device_role,'device_ip':netbox_device_ip,'device_status':netbox_device_status}})

#GET DEVICE INFORMATION FROM PRTG
list_prtg_devices = []
m = 0
dict_prtg_device_with_id = {}
for devices in prtg_get_devices['devices']:
    if devices['group'] != 'Local Probe' and devices['group'] != 'Root' and devices['group'] != 'Templates': 
        m+=1
        prtg_device_name = devices['device']
        prtg_device_role = devices['group']
        prtg_device_ip = devices['host']
        prtgobjid = devices['objid']
        dict_prtg_device_with_id[prtg_device_name] = prtgobjid
        #prtg_device_ip = devices['host']+'/32'
        prtg_device_status_long = devices['status']
        prtg_device_status_replace = re.match(r'\S+', prtg_device_status_long).group(0)
        if prtg_device_status_replace == 'Up':
            prtg_device_status = re.sub("Up","active",prtg_device_status_replace)
        elif prtg_device_status_replace == 'Paused':
            prtg_device_status = re.sub("Paused","offline",prtg_device_status_replace)
        list_prtg_devices.append({prtg_device_name:{'device_role':prtg_device_role,
        'device_ip':prtg_device_ip,'device_status':prtg_device_status}})

#COMPARE NETBOX AND PRTG LISTS
netbox_list = []
prtg_list = []
final_compared_list = []

#GET LIST WITH NETBOX NAMES
for netbox_dict in list_netbox_devices:
    for netbox_device,values in netbox_dict.items():
        netbox_list.append(netbox_device)

#GET LIST WITH PRTG NAMES
for prtg_dict in list_prtg_devices:
    for prtg_device in prtg_dict.keys():
        prtg_list.append(prtg_device)        

#GET DICTIONARIES TO ADD DEVICES IN PRTG FROM NETBOX
for netbox_final_dict in list_netbox_devices:
    for key_netbox in netbox_final_dict.keys():
        for netbox_list_device in netbox_list:
            if netbox_list_device not in prtg_list and key_netbox == netbox_list_device:
                print('look at this',netbox_final_dict)
                final_compared_list.append(netbox_final_dict)

#GET DICTINARIES TO DELETE DEVICE IN PRTG THAT'S NOT IN NETBOX    
dict_prtg_device_with_id
for device_in_prtg in prtg_list:
    if device_in_prtg not in netbox_list:
        object_id_delete = dict_prtg_device_with_id[device_in_prtg]
        print('now you can look in here',object_id_delete)
        url_prtg_delete = "{prtg_link}/api/deleteobject.htm?id={object_id_delete}&approve=1&username={username_prtg}&password={password_prtg}".format(object_id_delete=object_id_delete, prtg_link=prtg_link, username_prtg=username_prtg,password_prtg=password_prtg)
        create_new_object_prtg(url_prtg_delete)


#ADD DEVICES IN PRTG
for device_prtg in final_compared_list:
    for name_device in device_prtg.keys():
        new_device_name = name_device
        new_hostname_or_ip = device_prtg[name_device]['device_ip']
        if device_prtg[name_device]['device_role'] == 'Network':
            device_id = prtg_network_device_id
            id_of_target_group = prtg_network_group_id
            url_prtg_duplicate_device = "{prtg_link}/api/duplicateobject.htm?id={device_id}&name={new_device_name}&host={new_hostname_or_ip}&targetid={id_of_target_group}&username={username_prtg}&password={password_prtg}".format(device_id=device_id,new_device_name=new_device_name,new_hostname_or_ip=new_hostname_or_ip,id_of_target_group=id_of_target_group, prtg_link=prtg_link, username_prtg=username_prtg,password_prtg=password_prtg)
            create_new_object_prtg(url_prtg_duplicate_device)
        elif device_prtg[name_device]['device_role'] == 'Server':
            device_id = prtg_server_device_id
            id_of_target_group = prtg_group_server_id
            url_prtg_duplicate_device = "{prtg_link}/api/duplicateobject.htm?id={device_id}&name={new_device_name}&host={new_hostname_or_ip}&targetid={id_of_target_group}&username={username_prtg}&password={password_prtg}".format(device_id=device_id,new_device_name=new_device_name,new_hostname_or_ip=new_hostname_or_ip,id_of_target_group=id_of_target_group, prtg_link=prtg_link, username_prtg=username_prtg,password_prtg=password_prtg)
            create_new_object_prtg(url_prtg_duplicate_device)



        
#CHECK AGAIN THE DEVICES IN PRTG TO SEE IF THEIR ARE ACTIVE OR OFFLINE
prtg_get_devices = api_request(url=url_prtg)
for devices in prtg_get_devices['devices']:
    if devices['group'] != 'Local Probe' and devices['group'] != 'Root' and devices['group'] != 'Templates' : 
        prtg_device_status_long = devices['status']
        prtg_device_status_replace = re.match(r'\S+', prtg_device_status_long).group(0)
        if prtg_device_status_replace == 'Up':
            prtg_device_status = re.sub("Up","active",prtg_device_status_replace)
        elif prtg_device_status_replace == 'Paused':
            prtg_device_status = re.sub("Paused","offline",prtg_device_status_replace)
        for eachdict_netbox_device in list_netbox_devices:
            for each_netbox_device in eachdict_netbox_device.keys():
                prtg_device_name = devices['device']
                objid = devices['objid']
                device_netbox_status = eachdict_netbox_device[each_netbox_device]['device_status']
                if prtg_device_name == each_netbox_device and device_netbox_status != prtg_device_status:
                    if device_netbox_status == 'active':
                        url_prtg_resume_device = '{prtg_link}/api/pause.htm?id={objid}&action=1&username={username_prtg}&password={password_prtg}'.format(objid=objid, prtg_link=prtg_link, username_prtg=username_prtg,password_prtg=password_prtg)
                        print(url_prtg_resume_device)
                        resumeobj(url_prtg_resume_device)
                    elif device_netbox_status == 'offline':
                        url_prtg_resume_device = '{prtg_link}/api/pause.htm?id={objid}&action=0&username={username_prtg}&password={password_prtg}'.format(objid=objid, prtg_link=prtg_link, username_prtg=username_prtg,password_prtg=password_prtg)
                        print(url_prtg_resume_device)
                        resumeobj(url_prtg_resume_device)
