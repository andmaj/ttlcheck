# ttlcheck
Looking for irregular TTL modifier middleboxes with help of Planetlab

**You need to fill ssh_needs folder with your ssh key for Planetlab and change slice_name in scan.py if necessary**

## Usage

In one terminal (with root privileges):
```./ttlcheck <minttl> <diffttl> <interface>```

**Parameters:**

* **minttl**
Minimum accepted TTL
* **diffttl**
Required TTL difference
* **interface**
Ethernet interface name

In other terminal:
```./scan.py <ttl1> <ttl2> <ip> <filename>```

**Parameters:**

* **ttl1**
TTL of the first ping 
* **diffttl**
TTL of the second ping              
* **ip**
IP address to ping
* **filename**
File to save the results

**After scanning finished**
* **Type ```write <filename>``` into ttlcheck shell!**
* **Type ```quit``` into ttlcheck shell!**

Filter the results:
```./filter.sh <ttlcheck_filename> <scan_filename> <result_filename>```

Print summary:
```./summary.sh <result_filename>```

Print failed ones:
```./failed.sh <result_filename>```

Print succeed ones:
```./succeed.sh <result_filename>```
