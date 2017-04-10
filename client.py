#!/usr/bin/python

# Twisted Imports
from twisted.words.protocols.jabber import client, jid , xmlstream
from twisted.words.xish import domish
from twisted.internet import reactor

name = None
server = None
resource = None
password = None
me = None

thexmlstream = None
tryandregister = 1

def initOnline(xmlstream):
    # creamos los observadores hacia las respuestas xml message y una general (podemos incluir presence, iq...)
    global factory
    print 'Initializing...'
    xmlstream.addObserver('/message', gotMessage)
    xmlstream.addObserver('/*', gotSomething)

def authd(xmlstream):
    # Autentificacion
    global thexmlstream
    thexmlstream = xmlstream
    print "we've authd!"
    print repr(xmlstream)

    # se envia la presencia a los demas clientes
    presence = domish.Element(('jabber:client', 'presence'))
    presence.addElement('status').addContent('Online')
    xmlstream.send(presence)

    initOnline(xmlstream)

def send(author, to, msg):
    # esta funcion envia los mensajes
    global thexmlstream
    message = domish.Element(('jabber:client','message'))
    message["to"] = jid.JID(to).full()
    message["from"] = jid.JID(author).full()
    message["type"] = "chat"
    message.addElement("body", "jabber:client", msg+ "- ya lo sabia adicotalainformatica1")

    thexmlstream.send(message)

def gotMessage(el):
    # esta funcion parsea los mensajes recibidos
    global me
    # print 'Got message: %s' % str(el.attributes)
    from_id = el["from"]

    body = "empty"
    for e in el.elements():
        if e.name == "body":
            body = unicode(e.__str__())
        break

    send(me, from_id, body)

def gotSomething(el):
    # Observador general
    print 'Got something: %s -&gt; %s' % (el.name, str(el.attributes))

def authfailedEvent(xmlstream):
    global reactor
    print 'Auth failed!'
    reactor.stop()

def invaliduserEvent(self,xmlstream):
    print "Invalid User"

def registerfailedEvent(self,xmlstream):
    print 'Register failed!'

if __name__ == '__main__':
    # Parametrizamos la conexion
    PASSWORD = '123456'
    myJid = jid.JID('test_user@test-xmpp')
    me = 'test_user@test-xmpp'
    factory = client.XMPPClientFactory(myJid, PASSWORD)

    # Registramos las callbacks de autentificacion
    print 'register callbacks'
    factory.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, authd)
    factory.addBootstrap(client.BasicAuthenticator.INVALID_USER_EVENT, invaliduserEvent)
    factory.addBootstrap(client.BasicAuthenticator.AUTH_FAILED_EVENT, authfailedEvent)
    factory.addBootstrap(client.BasicAuthenticator.REGISTER_FAILED_EVENT, registerfailedEvent)

    # Paarametrizamos y arrancamos el reactor (encargado de mantener y gestionar las callbacks
    # producidas por las acciones de la conexion)
    reactor.connectTCP('localhost', 5222, factory)
    reactor.run()
