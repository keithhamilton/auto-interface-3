#!/usr/bin/python

from subprocess import check_output, call, STDOUT
from re import search
from os import system, path

def validate_hardware():
    hardware_specs=check_output(['/usr/sbin/system_profiler','SPHardwareDataType'], stderr=STDOUT)
    model = [x for x in hardware_specs if search('Model Name',x)] or ''
    return any('Mac Pro' in s for s in model)

def get_previous_state(flatfile_path, wireless_service,current_has_display_ethernet=False):
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

def get_all_services(wireless_service_name):
    all_services=check_output(['networksetup','-listallnetworkservices']).split('\n')[1:]
    return [x for x in all_services if search(wireless_service_name,x) or search('Ethernet',x)]

def get_service_state(service):
    service_details=[x for x in \
                     check_output(['networksetup', '-getinfo', '{0}'.format(service)]).split('\n') \
                     if search('10.0',x)]

    return 1 if len(service_details) > 0 else 0

def get_service_change(current, previous, wireless_service_name):
    '''
    Service State Examples:

    no action-------------------------------------------------

    # wireless turned on manually
    previous: {Ethernet: 0, Wi-Fi: 0, Display Ethernet: 0}
    current:  {Ethernet: 0, Wi-Fi: 1, Display Ethernet: 0}
    condition: bool(current['Wi-Fi'] and not(previous['Ethernet'] or previous['Wi-Fi']))

    # ethernet plugged in when nothing was on
    previous: {Ethernet: 0, Wi-Fi: 0, Display Ethernet: 0}
    current:  {Ethernet: 1, Wi-Fi: 0, Display Ethernet: 0}
    condition: bool(current['Ethernet'] and not (previous['Ethernet'] or previous['Wi-Fi']))

    # wireless turned off manually
    previous: {Ethernet: 0, Wi-Fi: 1, Display Ethernet: 0}
    current:  {Ethernet: 0, Wi-Fi: 0, Display Ethernet: 0}
    condition: bool(not (current['Wi-Fi'] or current['Ethernet']) and previous['Wi-Fi'])

    # -----------------------------------------------------------

    turn wireless off -----------------------------------------

    # ethernet plugged in when wi-fi was on
    previous: {Ethernet: 0, Wi-Fi: 1, Display Ethernet: 0}
    current:  {Ethernet: 1, Wi-Fi: 1, Display Ethernet: 0}
    condition: bool((current['Ethernet'] and current['Wi-Fi']) and not previous['Ethernet'])

    # -----------------------------------------------------------

    turn wireless on -----------------------------------------

    # ethernet unplugged when wi-fi was off
    previous: {Ethernet: 1, Wi-Fi: 0, Display Ethernet: 0}
    current:  {Ethernet: 0, Wi-Fi: 0, Display Ethernet: 0}
    condition: bool(previous['Ethernet'] and not (current['Ethernet'] or current['Wi-Fi']))
    '''

    if previous == current:
        return 'no_change'

    previous_ethernet = True in [val for key, val in previous.items() if search('Ethernet',key) and previous[key]]
    current_ethernet = True in [val for key, val in current.items() if search('Ethernet',key) and current[key]]

    if bool((current_ethernet and current[wireless_service_name]) and not previous_ethernet):
        return 'wireless_off'
    elif bool(previous_ethernet and not (current_ethernet or current[wireless_service_name])):
        return 'wireless_on'
    else:
        return 'no_change'


def get_hardware_device(service_name):
    port_info=check_output(['networksetup','-listallhardwareports']).split('\n')
    info = [port_info[i+1].split(': ')[1] for i,x in enumerate(port_info) if search(service_name,port_info[i])]
    return info[0] if len(info) > 0 else None

def toggle_wireless(wireless_service_name, turnOn=True):
    onOff='on'
    if not turnOn:
        onOff='off'

    service_device = get_hardware_device(wireless_service_name)
    call(['networksetup','-setairportpower',service_device,onOff])

def write_state(flatfile_path, current_service_state):
    f=open(flatfile_path, 'w')
    for key in current_service_state:
        f.write('%s:%s' % (key, current_service_state[key]))
        f.write('\n')
    f.close()

if __name__=='__main__':
    
    FLATFILE_PATH='/usr/local/lib/auto-interface-3/.previous-netstate'

    # get model. If model is Mac Pro, exit
    if not validate_hardware():
        system('exit')

    # get software (OS) version
    # if version is 10.6.x of lower, wireless service is named "Airport"
    # else, wireless service is named "Wi-Fi"
    sw_vers_info=check_output('sw_vers').split('\n')
    os_version=None

    os_version = [x for x in sw_vers_info if search('ProductVersion', x)][0]
    wireless_service = 'Airport' if int(os_version.split('\t')[1].split('.')[1]) <= 6 else 'Wi-Fi'

    #capture all current service states (wireless and any ethernet services)
    current_service_state = {x:get_service_state(x) for x in get_all_services(wireless_service)}

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