
network-insight-sdk-generic-datasources
=======================================

SDK is written to support as many physical devices so that vRNI can consume
network information in defined format. Network information includes Router Interfaces, VRFs, Switch Ports, 
Routes, etc. SDK can connect to physical device and execute commands. Output of command is then used to create
files in specific format (eg. CSV). Files generated are then bundled in ZIP format which can then be 
fed into vRNI. Driver in SDK is governed by YAML configuration file.

YAML configuration defines commands, parsers for command output, joiners for two different commands.

1. [ Dependencies ](#dependencies)
2. [ Launch SDK ](#launch-sdk)
3. [ Device Configuration File ](#zipfile)
4. [ YAML Configuration ](#yaml-configuration)
5. [ Parser Definition ](#parser-definition)
6. [ Table Joiner ](#table-joiner)

<a name="dependencies"></a>
## 1. Dependencies
* netmiko
* pylogger
* requests
* pyyaml

Install dependencies using following command.
```
pip install -r requirements.txt
```

<a name="launch-sdk"></a>
## 2. Launch SDK

After cloning this project and project folder in PYTHONPATH. Then run following command to run SDK.
```shell
$ python ./network-insight-sdk-generic-datasources/main.py -d <device> -m <model> -s <device_type> -i <ip-address> -u <username> -p <password>
```

> Command parameter explanation
- -d = the device which you want to run
- -m = model of device
- -s = List of device type as defined in network-insight-sdk-generic-datasources/connection/device_type.py
- -i = ip address or fqdn
- -u = username 
- -p = password

Example
```
$ git clone https://github.com/vmware/network-insight-sdk-generic-datasources.git
$ cd network-insight-sdk-generic-datasources
$ export PYTHONPATH="$PYTHONPATH:../network-insight-sdk-generic-datasources"
$ python ./network-insight-sdk-generic-datasources/main.py -d cisco -m n5k -s CISCO_IOS -i 10.1.1.1 -u test -p test

```

<a name="zipfile"></a>
## 3. Device Configuration File
SDK creates ZIP file as output. Zip file contains several CSV files of network entities. Each CSV has defined number of 
column headers. 

NOTE: General Guideline is to use double quotes for each value in a cell. Special characters allowed for any data, unless 
any defined values mentioned, are
as follows.
* _ Underscore
* \- Hyphen
* : Colon
* . Period
* \ Back Slash
* / Forward Slash

* switch.csv - contains switch information. MANDATORY

Column Name    | Mandatory / Optional | Description                    | Accepted Value
---------------| -------------------- | ------------------------------ | --------------
ipAddress/fqdn | mandatory            | ipAddress or FQDN of switch    | 
name           | mandatory            | name of the switch             | 
serial         | optional             | serial of the switch           |  
os             | optional             | operating system of the switch |
model          | optional             | model of the switch            |
vendor         | optional             | vendor of the switch           |
hostname       | optional             | hostname of the switch         |
haState        | mandatory            | redundant of the switch        | ACTIVE, STANDBY

* switch-ports.csv - contains all the switch ports and their attributes. MANDATORY

Column Name           | Mandatory / Optional | Description                    | Accepted Value
----------------------| -------------------- | ------------------------------ | -------------- 
name                  | mandatory            | name of switch port            | 
vlans                 | optional             | vlans                          | Comma separated Integer values (Note: use double quotes)
accessVlan            | optional             | accessVlan of switch port      | Integer Value
mtu                   | optional             | mtu                            | Integer Value
interfaceSpeed        | optional             | interface speed                | Integer Value in Bytes
operationalSpeed      | optional             | operational speed              | Integer Value in Bytes
administrativeStatus  | mandatory            | administrative status          | UP, DOWN
operationalStatus     | mandatory            | operational status             | UP, DOWN
hardwareAddress       | optional             | physical / mac address         | Mac Address for format(MM:MM:MM:SS:SS:SS or MM-MM-MM-SS-SS-SS or MMM.MMM.SSS.SSS)
duplex                | optional             | duplex                         | FULL, HALF
connected             | mandatory            | connected                      | TRUE, FALSE
switchPortMode        | mandatory            | switch port mode               | ACCESS, TRUNK, OTHER

* port-channels.csv - contains all the port channel (bundled switch ports) and their attributes. OPTIONAL


Column Name           | Mandatory / Optional | Description                    | Accepted Value
----------------------| -------------------- | ------------------------------ | -------------- 
name                  | mandatory            | name of the switch             | 
vlans                 | optional             | serial of the switch           |  
mtu                   | optional             | mtu                            | Integer Value
interfaceSpeed        | optional             | interface speed                | Integer Value in Bytes
operationalSpeed      | optional             | operational speed              | Integer Value in Bytes
administrativeStatus  | mandatory            | administrative status          | UP, DOWN
operationalStatus     | mandatory            | operational status             | UP, DOWN
hardwareAddress       | optional             | physical / mac address         | Mac Address for format(MM:MM:MM:SS:SS:SS or MM-MM-MM-SS-SS-SS or MMM.MMM.SSS.SSS)
duplex                | optional             | duplex                         | FULL, HALF
connected             | mandatory            | connected                      | TRUE, FALSE
switchPortMode        | mandatory            | switch port mode               | ACCESS, TRUNK, OTHER
activePorts           | optional             | active switch ports            | Interfaces defined in switch-ports.csv
passivePorts          | optional             | passive switch ports           | Interfaces defined in switch-ports.csv

* vrfs.csv - contains all vrfs of the switch/router. MANDATORY
    
Column Name           | Mandatory / Optional  | Description                    | Accepted Value
----------------------| --------------------- | ------------------------------ | -------------- 
name                  | mandatory             | name of the switch             | 

* router-interfaces.csv - contains all the router interfaces and their attributes. MANDATORY

Column Name           | Mandatory / Optional | Description                    | Accepted Value
----------------------| -------------------- | ------------------------------ | -------------- 
name                  | mandatory            | name of the switch             | 
vrf                   | mandatory            | vrf                            |  
vlan                  | optional             | vlan                           | Integer Value
ipAddress             | optional             | ip address of router interface | IP address
mtu                   | optional             | Mtu                            | Integer Value
interfaceSpeed        | optional             | Interface Speed                | Integer Value in Bytes
operationalSpeed      | optional             | Operational Speed              | Integer Value in Bytes
administrativeStatus  | mandatory            | Administrative Status          | UP, DOWN
operationalStatus     | mandatory            | Operational Status             | UP, DOWN
hardwareAddress       | optional             | physical / mac address         | Mac Address for format(MM:MM:MM:SS:SS:SS or MM-MM-MM-SS-SS-SS or MMM.MMM.SSS.SSS)
duplex                | optional             | Duplex                         | FULL, HALF
connected             | mandatory            | connected                      | TRUE, FALSE
loadBalancedProtocol  | optional             | Load Balanced Protocol         | VRRP, GLBP, HSRP, VARP, OTHER
loadBalancedStatus    | optional             | Load Balanced Status           | 1. VRRP -> INITIALIZE, MASTER, BACKUP. 2. GLBP -> ACTIVE, DISABLED, LISTEN, SPEAK, STANDBY, INITIAL. HSRP -> ACTIVE, INITIAL, LEARN, LISTEN, STANDBY, SPEAK. VARP -> ACTIVE. OTHER ->  ACTIVE, STANDBY  
loadBalancedIpAddress | optional             | Load balanced IP Address       | Interfaces defined in switch-ports.csv

* routes.csv - contains all routes. MANDATORY

Column Name           | Mandatory / Optional  | Description                    | Accepted Value
----------------------| --------------------- | ------------------------------ | -------------- 
name                  | mandatory             | name of route                  | 
network               | mandatory             | network of route               |  
nextHop               | mandatory             | next hop of route              | Use IP Address or DIRECT. If there is no nextHop ip address for direct routeType then use DIRECT. 
routeType             | mandatory             | route type eg. static, dynamic | Use Direct or any other routing protocol like OSPF, BGP, Static, etc. 
interfaceName         | mandatory             | interface name                 |
vrf                   | mandatory             | vrf                            |

* peer-devices.csv - contains list of redundant devices with respect the switch. OPTIONAL

Column Name           | Mandatory / Optional  | Description                    | Accepted Value
----------------------| --------------------- | ------------------------------ | -------------- 
peerIpAddress         | mandatory             | peer device ip address         | 
peerHostname          | mandatory             | peer device hostname           |

* neighbors.csv - contains list of LLDP/CDP neighbors. OPTIONAL

Column Name           | Mandatory / Optional  | Description                    | Accepted Value
----------------------| --------------------- | ------------------------------ | -------------- 
localInterface        | mandatory             | local switch port name         | Interfaces defined in switch-ports.csv
remoteDevice          | mandatory             | remote device ip/fqdn          |  
remoteInterface       | mandatory             | remote device interface        |

* mac-address-table.csv - contains mac address table. OPTIONAL

Column Name           | Mandatory / Optional  | Description                    | Accepted Value
----------------------| --------------------- | ------------------------------ | -------------- 
macAddress            | mandatory             | mac address                    | 
vlan                  | mandatory             | vlan                           |  
switchPort            | mandatory             | local switch port name         | Interfaces defined in switch-ports.csv

* l2bridges.csv - contains list of layer 2 (vlan) bridges. OPTIONAL

Column Name           | Mandatory / Optional  | Description                    | Accepted Value
----------------------| --------------------- | ------------------------------ | -------------- 
name                  | mandatory             | name of layer 2 bridge         | 
vlans                 | mandatory             | all the vlans of bridge        |

<a name="yaml-configuration"></a>
## 4. YAML Configuration

YAML configuration is defined in sections.
1. Command list - Contains command definition which needs to be run. Commands defined in top are executed first and one
defined in bottom is executed last.
* Each command definition has following items.
    * table_id - refer result with an id.
    * command - command to execute
    * block parser - Parser to parse blocks
    * parser - to parse each block, in any, otherwise full command output
    * pre_post_processor - If there is any custom handling required before and after parsing then it 
    can be defined. 
2. Table Joiner - Used for joining table. More information below.
3. Result writer - Used to write table, reference with table_id, to csv file.
    * Result writer accepts path parameter which tells in which directory csv files to generate.
4. Package Handler - Used to package files into a zip format.
    * Package Handler accepts path parameter which tells which directory to compress as zip.


<a name="parser-definition"></a>
## 5. Parser Definition

There are several kinds of parsers defined broadly defined in two categories
* Block Parsers - To parse command output where there is definite pattern of blocks reappearing every time.
    * SimpleBlockParser - Parses block if newline is present
    * LineBasedBlockParser - Similar to SimpleBlockParser but here you can specify line pattern (regex) reappearing.
        * Arguments
            * line_pattern
    * PatternBasedBlockParser - Similar to LineBasedBlockParser but here you can specify start_pattern and end_pattern
        * Arguments 
            * start_pattern
            * end_pattern
    * GenericBlockParser - It is wrapper of all other Block Parsers. Accepts parameter same as other block parsers.
        * Arguments - 
            * line_pattern 
            * start_pattern and end_pattern
    
* Text Parsers - Each blocks has fields which needs to be parsed.
    * Horizontal Table parser - Parses block in tabular format and creates list of key values.
        * Arguments 
            * skip_head - Number of lines to skip from start(top) of block
            * skip_tail - Number of lines to skip from end(bottom) of block
            * header_keys - Define Column headers names
    * Vertical Table parser - Parses data in vertical data format and creates list of key values.
        * Arguments 
            * skip_head - Number of lines to skip from start(top) of block
            * skip_tail - Number of lines to skip from end(bottom) of block
            * delimiter - Field delimiter. Default is colon
    * Generic Text Parser - Can parse block using regex pattern. Regex pattern must have group to select values.
        * Arguments - Contains variable arguments where argument name is the key to regex group value.
        For example, if we want to parse mtu value from text like `MTU 1500 Bytes`. In that case, we would define
        argument as `mtu: MTU (.*) Bytes` where `mtu` is key and regex would be `MTU (.*) Bytes`. Regex group value is 
        surrounded with parenthesis which will be parsed.
            


<a name="table-joiner"></a>
## 6. Table Joiner

Parsers create list of key value pairs which is logically in tabular format.
There are scenarios where we need to join two table having same column values.
Table joiner accept parameter as source table, source column, destination table and destination column.
Such table join can be considered as RIGHT join denoted by source_table RIGHT JOIN destination_table.

* SimpleTableJoiner - a table joiner which is able to join two tables (list for key value pairs) into a single table.


Contributing
============

Feel free to raise issues and send pull requests, we'll be happy to look at them!