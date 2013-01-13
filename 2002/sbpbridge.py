from twisted.protocols import toc, irc
from twisted.internet import tcp, main, reactor
import twisted.im.tocsupport as tit

class AIMBot(toc.TOCClient):
    def gotConfig(self, *args):
        self.add_deny([])
        self.add_buddy(['aaronswartz'])
        self.signon()

    def hearMessage(self, username, message, autoreply):
        if username != "aaronswartz": self.say(username, "Huh? Who do you think you are?"); return
        b2.msg("#sbp", tit.dehtml(message))

class IRCBot(irc.IRCClient):
    def signedOn(self):
        self.setNick("SeanP-AIM")
        self.join("#sbp")

    def ctcpQuery_ACTION(self, user, channel, data):
        b1.say("aaronswartz", "* " + user.split("!")[0]+" " + data)

    def privmsg(self, user, channel, message):
        if not user: print message; return
        b1.say("aaronswartz", "&lt;"+user.split("!")[0]+"&gt; "+message)

    def callWhois(self):
        print "calling whos"
        self.sendLine("WHOIS sbp")
        reactor.callLater(60, self.callWhois)

    def irc_RPL_WHOISIDLE(self, prefix, params):
        b1.idle(params[2])
        
b1 = AIMBot('screenname', 'password')
t1 = tcp.Client("toc.oscar.aol.com",9898,b1)

b2 = IRCBot()
t2 = tcp.Client("irc.openprojects.net", 6667, b2)

main.run()
