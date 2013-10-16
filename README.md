# auto-interface, v 0.3

creates launch agent on Mac OS X (10.6,10.7,10.8) that toggles 80211 service off when wired ethernet is plugged in, and turns 80211 on when wired ethernet is unplugged.  

## Getting Started
Download the .pkg file from this repo and install it. It adds the launch agent, and the executable, then runs it. After that, just behave normally, and let your IT staff know you're helping them out by not taking up two DHCP addresses at once.  

##Disclaimer  
This only works on OS X. Windows/Linux users, I'm sorry. This is a work-in-progress. Please list issues with at minimum a dump from this shell command: networksetup -listallnetworkservices  

## License
Copyright (c) 2013 Keith Hamilton  
Licensed under the MIT license.

## To-do  
update service capturing to be more dependent on actual active services instead of service names.
