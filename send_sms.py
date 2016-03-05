# regex learnt from: http://www.tutorialspoint.com/python/python_reg_expressions.htm
# socket programming code comes from: Computer.Networking.A.TopDown.Approach.6th.Edition Page167

from socket import *
from twilio.rest import TwilioRestClient
from time import sleep
import re
import random
import threading


import os
from flask import Flask
app = Flask(__name__)



# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC0fc5ed438e0d535fd192866592c20f8b"
auth_token  = "6c435a9bcf9b08c1113beada56be8696"
twilio_number = "+16072755283"
RECV_BUFFER = 2048
SERVER_NAME = '127.0.0.1'
SERVER_PORT = 6798
AUTH_CODE_MIN = 100000
AUTH_CODE_MAX = 999999
ERROR_MSG = "ERROR"
COUNT_DOWN_INIT_VALUE = 60 # seconds


# phone number -> frozen second count down
recent_sent_phone_numbers = {}


def listenAndSendSMS():
	client = TwilioRestClient(account_sid, auth_token)
	serverSocket = socket(AF_INET, SOCK_STREAM)
	# Prepare a server socket, use port 6789
	serverSocket.bind((SERVER_NAME, SERVER_PORT))
	serverSocket.listen(100)

	# start a background thread to count down
	stop_event= threading.Event()
	thread = threading.Thread(target = count_down, args = [stop_event])
	thread.start()

	lock = threading.Lock()
	
	while True:
		# naive synchronized implementation
		with lock:
		    print 'Ready to serve...'
		    connectionSocket, addr = serverSocket.accept()
		    try:
		        message = connectionSocket.recv(RECV_BUFFER)
		        matchObj = re.match( r'GET /\?phoneNumber=(.*) .*', message, re.M)

		        phoneNumber = matchObj.group(1)

		       	if not phone_number_valid(phoneNumber):
		        	continue
		        
		        phoneNumber = "+1" + phoneNumber

		        if phone_number_is_frozen(phoneNumber):
		        	continue 

		        recent_sent_phone_numbers[phoneNumber] = COUNT_DOWN_INIT_VALUE

		        auth_code = random.randrange(AUTH_CODE_MIN, AUTH_CODE_MAX)
		        msgBody = "Aloha, the authorization code is: "+str(auth_code)
		        msg = client.messages.create(body=msgBody,
				    to=phoneNumber,    
				    from_=twilio_number)

		        print msg.sid

		        # Send the HTTP status line and HTTP headers Content-Length and Content-Type into socket
		        # Fill in start
		        connectionSocket.send('HTTP/1.1 200 OK\r\n')
		        # size = sys.getsizeof(outputdata)
		        connectionSocket.send('Content-Length: ' + str(len(str(auth_code))) + '\r\n')
		        connectionSocket.send('Content-Type: text/html\r\n\r\n')
		        # print "msg shall been sent"
		        connectionSocket.send(str(auth_code))
		        connectionSocket.close()
		    except IOError:
		    	info = "<!DOCTYPE html><html><head><title>404 Not Found</title></head><body>404 Not Found</body></html>\r\n"

		        connectionSocket.send('HTTP/1.1 404 Not Found\r\n')
		        connectionSocket.send('Content-Length: ' + str(len(info)) + '\r\n')
		        connectionSocket.send('Content-Type: text/html\r\n\r\n')
		        connectionSocket.send(info)
		        connectionSocket.close()
	# stop the background thread. 
	stop_event.set()
	serverSocket.close()

# check the phone number is a valid phone
# return true if the number is valid, false otherwise
def phone_number_valid(phone_number):
	matchObj = re.match( r'^[0-9]{10}$', phone_number, )
	if matchObj is None:
		print phone_number, "is not valid"
		return False
	else:
		return True

# if the phone is in the frozen stage because twilio recently just send msg to it
# return true if the number is frozen, false otherwise
def phone_number_is_frozen(phone_number):
	if phone_number in recent_sent_phone_numbers:
		print phone_number, "is fronzen"
		print recent_sent_phone_numbers
		return True
	else:
		return False

# cound down of frozen time for phone just send twilior msg to
# when the count down reach 1, remove the phone_number from the frozen list
def count_down(stop_event):
	while (not stop_event.is_set()):
		sleep(1)
		for k, v in recent_sent_phone_numbers.items():
			if v <= 1:
				del recent_sent_phone_numbers[k]
			else:
				recent_sent_phone_numbers[k] -= 1

@app.route("/")
def hello():
    return "Hello from Python!"

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
	# recent_sent_phone_numbers["123"] = 10
	# stop_event= threading.Event()
	# thread = threading.Thread(target = count_down, args = [stop_event])
	# thread.start()
	
	print "hello"
	listenAndSendSMS()

