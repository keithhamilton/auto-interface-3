#!/usr/bin/python

from subprocess import check_output, call
from re import search
from os import system, path

def validate_hardware():
    hardware_specs=check_output(['/usr/sbin/system_profiler','SPHardwareDataType'])
    model=None

    # go through hardware specs and find the model name
    for item in hardware_specs:
        if search('Model Name:', item):
            model=item.split(': ')[1]

    if model == 'Mac Pro':
        return False

    return True

    #end function

def get_previous_state(flatfile_path, wireless_service,current_has_display_ethernet=False):
    print(current_has_display_ethernet)
    print(flatfile_path)
    previous_service_state = {}

    if path.exists(flatfile_path):
        f=open(flatfile_path,'r')
        for item in f.readlines():
            previous_service_state[item.rstrip().split(':')[0]] = int(item.rstrip().split(':')[1])
        f.close()
    else:
        previous_service_state = {'Ethernet':0,wireless_service:0}
        if current_has_display_ethernet:
            previous_service_state['Display Ethernet'] = 0
    
    return previous_service_state

    #end function

def get_all_services(wireless_service_name):
    all_services=check_output(['networksetup','-listallnetworkservices']).split('\n')[1:]
    net_services=[]

    for item in all_services:
        if search(wireless_service_name,item) or search('Ethernet',item):
            net_services.append(item)

    return net_services

    #end function

def get_service_state(service):
    # try:
    service_details=check_output(['networksetup', '-getinfo', '{0}'.format(service)]).split('\n')
    for item in service_details:
        if search('10.0.', item):
            return 1
    return 0
    # except:
    #     return 0

    #end function

def get_service_change(current, previous, wireless_service_name):

    if previous == current:
        return 'no_change'

    previousEthernetServices = []
    previous_ethernet = False
    currentEthernetServices = []
    current_ethernet = False

    for service in previous:
        if search('Ethernet', service):
            previousEthernetServices.append(service)
    for service in previousEthernetServices:
        previous_ethernet = previous_ethernet or previous[service]

    for service in current:
        if search('Ethernet', service):
            currentEthernetServices.append(service)
    for service in currentEthernetServices:
        current_ethernet = current_ethernet or current[service]


    #previous_ethernet = previous['Ethernet']
    #if 'Display Ethernet' in previous.keys():
    #   previous_ethernet = previous_ethernet or previous['Display Ethernet']
    #current_ethernet = current['Ethernet']
    #if 'Display Ethernet' in current.keys():
    #    current_ethernet = current_ethernet or current['Display Ethernet']

    if bool((current_ethernet and current['Wi-Fi']) and not previous_ethernet):
        return 'wireless_off'
    elif bool(previous_ethernet and not (current_ethernet or current['Wi-Fi'])):
        return 'wireless_on'
    else:
        return 'no_change'

    # Service State Examples:

    # no action-------------------------------------------------
    
    ## wireless turned on manually
    # previous: {Ethernet: 0, Wi-Fi: 0, Display Ethernet: 0}
    # current:  {Ethernet: 0, Wi-Fi: 1, Display Ethernet: 0}
    # condition: bool(current['Wi-Fi'] and not(previous['Ethernet'] or previous['Wi-Fi']))

    ## ethernet plugged in when nothing was on
    # previous: {Ethernet: 0, Wi-Fi: 0, Display Ethernet: 0}    
    # current:  {Ethernet: 1, Wi-Fi: 0, Display Ethernet: 0}
    # condition: bool(current['Ethernet'] and not (previous['Ethernet'] or previous['Wi-Fi']))
    
    ## wireless turned off manually
    # previous: {Ethernet: 0, Wi-Fi: 1, Display Ethernet: 0}
    # current:  {Ethernet: 0, Wi-Fi: 0, Display Ethernet: 0} 
    # condition: bool(not (current['Wi-Fi'] or current['Ethernet']) and previous['Wi-Fi'])

    # -----------------------------------------------------------

    # turn wireless off -----------------------------------------
    
    ## ethernet plugged in when wi-fi was on
    # previous: {Ethernet: 0, Wi-Fi: 1, Display Ethernet: 0}
    # current:  {Ethernet: 1, Wi-Fi: 1, Display Ethernet: 0}
    # condition: bool((current['Ethernet'] and current['Wi-Fi']) and not previous['Ethernet'])

    # -----------------------------------------------------------

    # turn wireless on -----------------------------------------
    
    ## ethernet unplugged when wi-fi was off
    # previous: {Ethernet: 1, Wi-Fi: 0, Display Ethernet: 0}
    # current:  {Ethernet: 0, Wi-Fi: 0, Display Ethernet: 0}
    # condition: bool(previous['Ethernet'] and not (current['Ethernet'] or current['Wi-Fi']))

    #end function

def get_hardware_device(service_name):
    port_info=check_output(['networksetup','-listallhardwareports']).split('\n')
    i=0
    while i<len(port_info):
            if search(service_name,port_info[i]):
                    return port_info[i+1].split(': ')[1]
            else:
                    i+=1   

    #end function

def toggle_wireless(wireless_service_name, turnOn=True):
    onOff='on'
    if not turnOn:
        onOff='off'

    service_device = get_hardware_device(wireless_service_name)
    system('networksetup -setairportpower {0} {1}'.format(service_device,onOff))

    #end function

def write_state(flatfile_path, current_service_state):
    f=open(flatfile_path, 'w')
    for key in current_service_state:
        f.write('{0}:{1}'.format(key, current_service_state[key]))
        f.write('\n')
    f.close()

    #end function

if __name__=='__main__':
    
    FLATFILE_PATH='/Users/.previous_netstate'

    # get model. If model is Mac Pro, exit
    if not validate_hardware():
        system('exit')

    # get software (OS) version
    # if version is 10.6.x of lower, wireless service is named "Airport"
    # else, wireless service is named "Wi-Fi"
    sw_vers_info=check_output('sw_vers').split('\n')
    os_version=None
    wireless_service='Wi-Fi'

    for item in sw_vers_info:
        if search('ProductVersion',item):
            os_version=item.split('\t')[1].split('.')[1]
    
    if int(os_version) <= 6:
        wireless_service='Airport'


    #capture all current service states (wireless and any ethernet services)
    current_service_state = {}

    service_list = get_all_services(wireless_service)
    for service in service_list:
        current_service_state[service] = get_service_state(service)

    #read in previous state from flatfile
    previous_service_state=get_previous_state(FLATFILE_PATH, wireless_service, 'Display Ethernet' in current_service_state.keys())
    
    # get the needed change based on a comparison between previous and current states
    service_change = get_service_change(current_service_state, previous_service_state, wireless_service)

    if service_change == 'wireless_on':
        current_service_state[wireless_service] = 1
        toggle_wireless(wireless_service)
    elif service_change == 'wireless_off':
        current_service_state[wireless_service] = 0
        toggle_wireless(wireless_service, False)
    else:
        pass

    # write the state to the flatfile for next time
    write_state(FLATFILE_PATH,current_service_state)

    # GTFO
    system('exit')