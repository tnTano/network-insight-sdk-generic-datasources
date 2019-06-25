# Copyright 2019 VMware, Inc.
# SPDX-License-Identifier: BSD-2-Clause


import re
import traceback

from network_insight_sdk_generic_datasources.common.utilities import merge_dictionaries
from network_insight_sdk_generic_datasources.common.log import py_logger
from network_insight_sdk_generic_datasources.parsers.text.pre_post_processor import PrePostProcessor
from network_insight_sdk_generic_datasources.parsers.common.block_parser import SimpleBlockParser
from network_insight_sdk_generic_datasources.parsers.common.text_parser import GenericTextParser
from network_insight_sdk_generic_datasources.parsers.common.block_parser import LineBasedBlockParser
from network_insight_sdk_generic_datasources.parsers.common.line_parser import LineTokenizer


class JuniperChassisPrePostProcessor(PrePostProcessor):

    def pre_process(self, data):
        output_lines = []
        block_parser = SimpleBlockParser()
        blocks = block_parser.parse(data)
        for block in blocks:
            if 'node0' in block:
                lines = block.splitlines()
                output_lines.append('hostname: {}'.format(lines[2].split(' ')[-1]))
                output_lines.append('name: Juniper {}'.format(lines[3].split(' ')[-1]))
                output_lines.append('os: JUNOS {}'.format(lines[4].split(' ')[-1]))
                output_lines.append('model: {}'.format(lines[3].split(' ')[-1]))
            output_lines.append('ipAddress/fqdn: 10.40.13.37')
        output_lines.append('vendor: Juniper')
        return '\n'.join(output_lines)

    def post_process(self, data):
        return [merge_dictionaries(data)]


class JuniperConfigInterfacesPrePostProcessor(PrePostProcessor):

    def post_process(self, data):
        result = []
        if data[0].has_key("vlan"):
            result.append(data[0])
        return result


class JuniperDevicePrePostProcessor(PrePostProcessor):

    def pre_process(self, data):
        output_lines = []
        block_parser = SimpleBlockParser()
        blocks = block_parser.parse(data)
        for block in blocks:
            if 'node0' in block:
                lines = block.splitlines()
                output_lines.append('hostname: {}'.format(lines[2].split(' ')[-1]))
                output_lines.append('name: Juniper {}'.format(lines[3].split(' ')[-1]))
                output_lines.append('os: JUNOS {}'.format(lines[4].split(' ')[-1]))
                output_lines.append('model: {}'.format(lines[3].split(' ')[-1]))
        output_lines.append('ipAddress/fqdn: 10.40.13.37')
        output_lines.append('vendor: Juniper')
        return '\n'.join(output_lines)

    def post_process(self, data):
        return [merge_dictionaries(data)]


class JuniperInterfacePrePostProcessor(PrePostProcessor):
    physical_regex_rule = dict(mtu=".*Link-level type: .*, MTU: (.*?),", name="Physical interface: (.*), Enabled.*",
                               hardwareAddress=".*Current address: .*, Hardware address: (.*)",
                               operationalStatus=".*, Enabled, Physical link is (.*)",
                               administrativeStatus="Physical interface: .*, (.*), Physical link is .*")
    logical_interface_regex = dict(name="Logical interface (.*) \(Index .*", ipAddress=".*Local: (.*), Broadcast:.*",
                                   mask=".*Destination: (.*), Local:.*")

    skip_interface_names = [".local.", "fxp1", "fxp2", "lo0"]

    def pre_process(self, data):
        try:
            output_lines = []
            generic_parser = GenericTextParser()
            physical = generic_parser.parse(data, self.physical_regex_rule)[0]
            physical.update({'connected': "TRUE" if physical['operationalStatus'] == "Up" else "FALSE"})
            physical.update({'operationalStatus': "UP" if physical['operationalStatus'] == "Up" else "DOWN"})
            physical.update({'administrativeStatus': "UP" if physical['administrativeStatus'] == "Enabled" else "DOWN"})
            physical.update({'hardwareAddress': "" if physical['hardwareAddress'].isalpha() else physical['hardwareAddress']})
            if physical['name'].rstrip() in self.skip_interface_names: return ""

            parser = LineBasedBlockParser('Logical interface')
            blocks = parser.parse(data)
            for block in blocks:
                logical = generic_parser.parse(block, self.logical_interface_regex)[0]
                physical.update({"ipAddress": "{}/{}".format(logical['ipAddress'], logical['mask'].split('/')[1]) if logical['ipAddress'] else ""})
                physical.update({"members": "{}".format(self.get_members(block))})
                physical.update({"name": "{}".format(logical['name'] if logical['name'] else physical['name'])})
                output_line = "\n".join(["{}:{}".format(i, j) for i, j in physical.iteritems()])
                output_lines.append(output_line)
        except Exception as e:
            py_logger.error("{}\n{}".format(e, traceback.format_exc()))
            raise e
        return '\n\n'.join(output_lines)

    def post_process(self, data):
        result = []
        for d in data:
            temp = {}
            for i in d.split('\n'):
                val = i.split(':')
                temp[val[0]] = val[1]
            result.append(temp)
        return result

    @staticmethod
    def get_members(block_1):
        result = ""
        got_members = False
        lines = []
        for i in block_1.splitlines():
            if "Link:" in i:
                lines = []
                continue
            if "Marker Statistics" in i:
                got_members = True
                break
            lines.append(i)
        if got_members:
            result = ",".join([mem for mem in lines if "Input" not in mem and "Output" not in mem])
        return result


class JuniperSwitchPortTableProcessor():

    def process_tables(self, tables):
        result = []
        vlan_interface = ["{}.{}".format(i['interface'], i['unit']) for i in tables['showConfigInterface']]
        for port in tables['showInterface']:
            port["switchPortMode"] = "TRUNK" if port['name'] in vlan_interface else "ACCESS"
            port["vlan"] = port['name'].split('.')[1] if port['name'] in vlan_interface else "0"
            result.append(port)
        return result


class JuniperRouterInterfaceTableProcessor():

    def process_tables(self, result_map):
        columns = ["name", "vlan", "administrativeStatus", "switchPortMode", "mtu", "operationalStatus", "connected",
                   "hardwareAddress", "vrf"]

        result = []
        for port in result_map['showInterface']:
            temp = {}
            add_entry = False
            for vrf in result_map['vrfs']:
                if vrf.has_key("interfaces"):
                    if port['name'] in vrf['interfaces']:
                        temp['vrf'] = vrf['name']
                        break
                else:
                    temp['vrf'] = "master"
            for i, j in port.iteritems():
                if i in columns:
                    add_entry = True if i == "ipAddress" and j else add_entry
                    temp[i] = j
            if add_entry: result.append(temp)
        return result


class JuniperPortChannelTableProcessor():

    def process_tables(self, result_map):
        result = []
        for port in result_map['showInterface']:
            temp = {}
            add_entry = False
            for i, j in port.iteritems():
                add_entry = True if i == "members" and j else add_entry
                temp[i] = j
            if add_entry:
                result.append(temp)
        return result


class JuniperRoutesPrePostProcessor(PrePostProcessor):

    def pre_process(self, data):
        try:
            output_lines = []
            parser = LineBasedBlockParser('(.*): \d* destinations')
            blocks = parser.parse(data)
            next_hop = "Next hop: (.*) via"
            next_hop_type = ".*Next hop type: (.*?), .*"
            interface = ".* via (.*),"
            network_name_regex = "(.*) \(.* ent"
            route_type = "\*?(\w+)\s+Preference:.*"
            network_interface = "Interface: (.*)"
            rules = dict(next_hop=next_hop, next_hop_type=next_hop_type, interface=interface,
                         route_type=route_type, network_interface=network_interface)
            for block in blocks:
                if not block: continue
                vrf = self.get_pattern_match(block, '(.*): \d* destinations')
                block_parser_1 = SimpleBlockParser()
                blocks_1 = block_parser_1.parse(block)
                for block_1 in blocks_1:
                    parser = LineBasedBlockParser(route_type)
                    line_blocks = parser.parse(block_1)
                    for idx, line_block in enumerate(line_blocks):
                        if 'inet' in line_block:
                            if 'announced' in line_block:
                                network_name = self.get_pattern_match(line_block.splitlines()[1], network_name_regex)
                            continue
                        if 'announced' in line_block:
                            network_name = self.get_pattern_match(line_block, network_name_regex)
                            continue
                        if ":" in network_name: continue  # checking skipping if interface is iv6
                        parser = GenericTextParser()
                        output = parser.parse(line_block, rules)
                        if ":" in output[0]['next_hop_type'] == "Receive": continue
                        vrf = "master" if vrf == "inet.0" else vrf.split('.inet.0')[0]
                        output_vrf = "vrf: {}".format(vrf)
                        if 'interface' in output[0].keys():
                            output_interface_name = "interfaceName: {}".format(output[0]['interface'])
                        elif 'network_interface' in output[0].keys():
                            output_interface_name = "interfaceName: {}".format(output[0]['network_interface'])
                        else:
                            continue
                        name = "name: {}_{}".format(network_name, idx)
                        output_route_type = "routeType: {}".format(output[0]['route_type'])
                        output_next_hop = "nextHop: {}".format(output[0]['next_hop'] if "next_hop" in output[0].keys()
                                                               else "DIRECT")
                        if "next_hop" not in output[0].keys():   # Temporary fix for STATIC and LOCAL
                            output_route_type = "routeType: {}".format("DIRECT")
                        output_network = "network: {}".format(network_name)
                        output_line = "{}\n{}\n{}\n{}\n{}\n{}\n".format(output_vrf, output_network, output_route_type,
                                                                        output_next_hop, output_interface_name, name)
                        output_lines.append(output_line)
        except Exception as e:
            py_logger.error("{}\n{}".format(e, traceback.format_exc()))
            raise e
        return '\n'.join(output_lines)

    def post_process(self, data):
        result = []
        for d in data:
            temp = {}
            for i in d.split('\n'):
                val = i.split(': ')
                temp[val[0]] = val[1] if len(val) > 1 else ""
            result.append(temp)
        return result

    @staticmethod
    def get_pattern_match(line_block, pattern):
        match_pattern = re.compile(pattern)
        match = match_pattern.match(line_block.strip())
        return match.groups()[0]


class JuniperMACTablePrePostProcessor(PrePostProcessor):

    def post_process(self, data):
        result = []
        for d in data:
            temp = {}
            for port in data["switch-ports"]:
                if d['switchPort'] == port['name']:
                    temp['vlan'] = port['vlan']
                    for i in d:
                        temp[i] = d[i]
                    result.append(temp)
                    break
        return result


class JuniperVRFPrePostProcessor(PrePostProcessor):

    def post_process(self, data):
        result = []
        for d in data:
            if d:
                temp = {}
                vrf_data = d.splitlines()
                router_id = vrf_data[1].split(":")[1].lstrip()
                if "0.0.0.0" == router_id: continue
                vrf_name = vrf_data[0].split(':')[0]
                temp['name'] = "{}".format(vrf_name)
                if "Interfaces:" in d:
                    interfaces = []
                    got_interface = False
                    for i in vrf_data:
                        if "Interfaces:" == i:
                            got_interface = True
                            interfaces = []
                            continue
                        if ":" in i and got_interface:
                            break
                        interfaces.append(i)
                    temp['interfaces'] = ",".join(interfaces)
                result.append(temp)
        return result


class JuniperNeighborsTablePrePostProcessor(PrePostProcessor):

    def pre_process(self, data):
        output_lines = []
        for line in data.splitlines()[1:]:
            if "Local Interface" in line: continue
            line_tokenizer = LineTokenizer()
            line_token = line_tokenizer.tokenize(line)
            local_interface = "localInterface: {}".format(line_token[0])
            remote_interface = "remoteInterface: {}".format(line_token[5])  # taking only port name
            remote_device = "remoteDevice: {}".format(line_token[-1])
            output_line = "{}\n{}\n{}\n".format(local_interface, remote_device, remote_interface)
            output_lines.append(output_line)
        return '\n'.join(output_lines)

    def post_process(self, data):
        result = []
        for d in data:
            temp = {}
            for i in d.split('\n'):
                val = i.split(': ')
                temp[val[0]] = val[1] if len(val) > 1 else ""
            result.append(temp)
        return result
