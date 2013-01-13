from twisted.protocols import toc, irc
from twisted.internet import reactor
import twisted.im.tocsupport as tit

class AIMBot(toc.TOCClient):
    def gotConfig(self, *args):
        self.add_deny([])
        self.add_buddy(['aaronswartz'])
        self.signon()

    def hearMessage(self, username, message, autoreply):
        if username != "aaronswartz":
            self.say(username, "Huh? Who do you think you are?"); return
        b2.msg("#sbp", "<"+username+"> " + tit.dehtml(message))

class IRCBot(irc.IRCClient):
    def signedOn(self):
        self.setNick("AaronSw-AIM")
        self.join("#sbp")

    def ctcpQuery_ACTION(self, user, channel, data):
        b1.say("aaronswartz", "* " + user.split("!")[0]+" " + data)

    def privmsg(self, user, channel, message):
        if not user: print message; return
        b1.say("aaronswartz", "&lt;"+user.split("!")[0]+"&gt; "+message)

b1 = AIMBot('username', 'password')
reactor.clientTCP("toc.oscar.aol.com",9898,b1)

b2 = IRCBot()
reactor.clientTCP("irc.openprojects.net", 6667, b2)

reactor.run()
