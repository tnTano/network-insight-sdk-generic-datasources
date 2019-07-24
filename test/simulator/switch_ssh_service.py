from twisted.conch import avatar, recvline
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import factory, keys, session
from twisted.conch.insults import insults
from twisted.cred import portal, checkers
from twisted.internet import reactor
from zope.interface import implements
import logging

class SSHProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.write("Welcome to my test SSH server.")
        self.terminal.nextLine()
        self.do_help()
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write("$ ")

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    def lineReceived(self, line):
        line = line.strip()
        if line:
            print line
            f = open('logfile.log', 'w')
            f.write(line + '\n')
            f.close
            cmdAndArgs = line.split()
            cmd = cmdAndArgs[0]
            args = cmdAndArgs[1:]
            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(*args)
                except Exception, e:
                    self.terminal.write("Error: %s" % e)
                    self.terminal.nextLine()
            else:
                self.terminal.write("No such command.")
                self.terminal.nextLine()
        self.showPrompt()

    def do_help(self):
        publicMethods = filter(
                lambda funcname: funcname.startswith('do_'), dir(self))
        commands = [cmd.replace('do_', '', 1) for cmd in publicMethods]
        self.terminal.write("Commands: " + " ".join(commands))
        self.terminal.nextLine()

    def do_echo(self, *args):
        self.terminal.write(" ".join(args))
        self.terminal.nextLine()

    def do_whoami(self):
        self.terminal.write(self.user.username)
        self.terminal.nextLine()

    def do_show(self, *args):
        raise NotImplementedError()

    def do_quit(self):
        self.terminal.write("Thanks for playing!")
        self.terminal.nextLine()
        self.terminal.loseConnection()

    def do_clear(self):
        self.terminal.reset()


class SSHAvatar(avatar.ConchUser):
    implements(ISession)

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(SSHProtocol, self)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, cmd):
        raise NotImplementedError()

    def closed(self):
        pass


class SSHRealm(object):
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            return interfaces[0], SSHAvatar(avatarId), lambda: None
        else:
            raise NotImplementedError("No supported interfaces found.")

def getRSAKeys():
    with open('id_rsa') as privateBlobFile:
        privateBlob = privateBlobFile.read()
        privateKey = keys.Key.fromString(data=privateBlob)

    with open('id_rsa.pub') as publicBlobFile:
        publicBlob = publicBlobFile.read()
        publicKey = keys.Key.fromString(data=publicBlob)
    return publicKey, privateKey


class SwitchSshService():
    def __init__(self, ip=None, port=22, switch_core=None, users=None):
        self.ip = ip
        self.port = port
        self.switch_core = switch_core
        self.users = users

    def hook_to_reactor(self, reactor):
        ssh_factory = factory.SSHFactory()
        sshFactory.portal = portal.Portal(SSHRealm())
        ssh_factory.portal = portal.Portal(SSHRealm(self.switch_core))
        if not self.users:
            self.users = {'root': b'root'}
        ssh_factory.portal.registerChecker(
            checkers.InMemoryUsernamePasswordDatabaseDontUse(**self.users))

        host_public_key, host_private_key = getRSAKeys()
        ssh_factory.publicKeys = {
            b'ssh-rsa': keys.Key.fromString(data=host_public_key.encode())}
        ssh_factory.privateKeys = {
            b'ssh-rsa': keys.Key.fromString(data=host_private_key.encode())}

        lport = reactor.listenTCP(port=self.port, factory=ssh_factory, interface=self.ip)
        logging.info(lport)
        logging.info(
            "%s (SSH): Registered on %s tcp/%s" % (self.switch_core.switch_configuration.name, self.ip, self.port))
        return lport


if __name__ == "__main__":
    sshFactory = factory.SSHFactory()


users = {'admin': b'aaa', 'guest': b'bbb'}
sshFactory.portal.registerChecker(
        checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))
pubKey, privKey = getRSAKeys()
sshFactory.publicKeys = {'ssh-rsa': pubKey}
sshFactory.privateKeys = {'ssh-rsa': privKey}
reactor.listenTCP(22331, sshFactory)
reactor.run()