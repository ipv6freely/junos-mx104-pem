# junos-mx104-pem

A script used for updating a list of MX104 routers with an event script to address Juniper PR1064039

## Description

DC-PEMs of MX104 systems may suddenly restart due to over temperature protection and can trigger a system restart. The DC-PEM temperature sensors were not monitored by the fan system algorithm causing over-temperature conditions under certain environmental conditions.  MX104 with AC-PEMs are not exposed.

(https://prsearch.juniper.net/InfoCenter/index?page=prcontent&id=PR1064039)

## Usage

1. Create a file named mx103-list.input.txt that contains a list of IP addresses or FQDNs of all of your MX104 routers
2. Run the script: 
```
python junos-mx104-pem.py
```

## Author
* **Chris Jones** - Github: [IPv6Freely](https://github.com/ipv6freely) - Twitter: [@IPv6Freely](https://twitter.com/ipv6freely)

## Credits

* JTAC Created the monitoring-pem.slax script
