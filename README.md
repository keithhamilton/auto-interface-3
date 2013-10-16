# gs-ldap-update

consumes google spreadsheet data for use with custom LDAP update endpoint

## Getting Started
Install the command-line utility with `git clone https://github.com/wieden-kennedy/gs-ldap-update`

```javascript
cd gs-ldap-update  
npm install  
node lib/index.js [--debug=true] [--config-file path/to/config/file] [--generate-credentials=true] [--username='googledocs.email@domain.com'] [--password='s0mep@ssw0rd']
```

## Documentation
###Config File  
The config file is the heart of running this program, where the Google spreadsheet information and the endpoint connection information is kept.  

###Credentials
The first time you run this you will want to pass the --generate-credentials=true flag along with the username and password flags and their respective values (the u/p for the Google spreadsheet) in addition to the --config-file flag. You can try to run it without doing this, but it will fail.  

## License
Copyright (c) 2013 Keith Hamilton  
Licensed under the MIT license.

## To-do  
Pull key fields for lib/ldap-util/index.js from sheet into config options for more flexibility
