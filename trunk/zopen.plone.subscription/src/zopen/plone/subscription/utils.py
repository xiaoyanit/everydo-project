from Crypto.Cipher import AES
from binascii import a2b_base64, b2a_base64, hexlify, unhexlify
import base64

aes = AES.new('0zopen 1is 2powe', AES.MODE_ECB) 

def generateTicket(*args):
    raw_ticket = ' '.join(args)
    raw_ticket += ' '*(16 - len(raw_ticket) % 16)
    encrytped_ticket = aes.encrypt(raw_ticket)
    print base64.b64encode(encrytped_ticket)
    return b2a_base64(encrytped_ticket)[:-1].replace('+', '-').replace('/', '_')

def parseTicket(ticket):
    ticket = ticket.replace('-', '+').replace('_', '/')
    ticket = a2b_base64(ticket)
    return aes.decrypt(ticket).rstrip().split()

def getUnsubURL(email):
    email = email.lower().strip()
    ticket = generateTicket(email, 'u')
    ticketurl = 'http://everydo.com/newsletter/@@subconfirm?id=%s' % ticket
    return ticketurl

if __name__ == '__main__':
    args = ('99000',)
    ticket = generateTicket(*args)
    print ticket, len(ticket)
    print parseTicket(ticket)

