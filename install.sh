#!/bin/bash


FLATFILE='/usr/local/lib/auto-interface-3/.previous-netstate'
TMP_DIR='/tmp/auto-interface-3'
DEST_PATH='usr/local/sbin/ai3.py'
PLIST_PATH='Library/LaunchAgents'

# clone the repository down
git clone https://github.com/keithhamilton/auto-interface-3 ${TMP_DIR}

# make the lib directory if it doesn't exist
if [ ! -e /usr/local/lib/auto-interface-3 ]; then
    sudo mkdir -p /usr/local/lib/auto-interface-3
    chmod 777 /usr/local/lib/auto-interface-3
fi

# remove any existing versions of auto-interface
if [ -e /usr/sbin/ai3.py ]; then
    sudo rm /usr/sbin/ai3.py
fi

# remove legacy netstate file, if present
if [ -e /Users/.previous-netstate ]; then
    rm /Users/.previous-netstate
fi

if [ ! -e /usr/local/sbin ]; then
    sudo mkdir /usr/local/sbin
fi
# copy ai3.py into place
sudo cp ${TMP_DIR}/src/${DEST_PATH} /${DEST_PATH}

# delete any existing autointerface launchd plists from previous installs
sudo rm /Library/LaunchAgents/*autointerface*

# cat out the launchd plist replacing the domain of the process
cat ${TMP_DIR}/src/${PLIST_PATH}/local.autointerface3.plist | sed 's/local\.autointerface3/com\.keithhamilton\.autointerface3/' > ${TMP_DIR}/com.keithhamilton.autointerface3.plist
sudo mv ${TMP_DIR}/com.keithhamilton.autointerface3.plist /${PLIST_PATH}
sudo chmod 644 /${PLIST_PATH}/com.keithhamilton.autointerface3.plist
launchctl load /${PLIST_PATH}/com.keithhamilton.autointerface3.plist

# remove tmp dir
sudo rm -rf ${TMP_DIR}

# run ai3.py
python /${DEST_PATH}
