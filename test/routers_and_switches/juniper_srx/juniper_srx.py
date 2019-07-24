
from test.simulator.switch_ssh_service import SwitchSshService

class EnabledCommandProcessor(SwitchSshService):
    def __init__(self, config):
        super(EnabledCommandProcessor, self).__init__()

    def do_show(self, *args):
        if "lldp neighbors" in " ".join(args):
            with open("{}/show_lldp_neighbor.txt".format(os.getcwd())) as f:
                for line in f.readlines():
                    self.terminal.write(line)
        elif "version" in " ".join(args):
            with open("{}/show_version.txt".format(os.getcwd())) as f:
                for line in f.readlines():
                    self.terminal.write(line)
        elif "interfaces detail" in " ".join(args):
            with open("{}/show_interfaces_detail.txt".format(os.getcwd())) as f:
                for line in f.readlines():
                    self.terminal.write(line)
        elif "chassis hardware" in " ".join(args):
            with open("{}/chasis.xml".format(os.getcwd())) as f:
                self.terminal.write(f.read())
        elif "route detail" in " ".join(args):
            with open("{}/show_route.txt".format(os.getcwd())) as f:
                for line in f.readlines():
                    self.terminal.write(line)
        elif "arp no-resolve" in " ".join(args):
            with open("{}/show_arp_no_resolve_mac_table.txt".format(os.getcwd())) as f:
                for line in f.readlines():
                    self.terminal.write(line)
        elif "route instance detail" in " ".join(args):
            with open("{}/show_route_instance_detail.txt".format(os.getcwd())) as f:
                for line in f.readlines():
                    self.terminal.write(line)
        elif "configuration interfaces" in " ".join(args):
            with open("{}/show_configuration_interfaces.txt".format(os.getcwd())) as f:
                for line in f.readlines():
                    self.terminal.write(line)