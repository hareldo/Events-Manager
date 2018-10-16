#!/usr/bin/python


from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import os
import subprocess
import cgi
import json
import pickle
from eventsDic import eventsDic

PORT_NUMBER = 8080
FILES_FOLDER = r"C:\\events\\"

mimetypes = {}
mimetypes[".html"] = "text/html"
mimetypes[".jpg"] = "image/jpg"
mimetypes[".gif"] = "text/gif"
mimetypes[".js"] = "application/javascript"
mimetypes[".css"] = "text/css"

# All form data will be stored in here.
eventsFile = 'eventsDic.py'

def saveState():
	f = open(eventsFile, "w")
	f.write("eventsDic = ")
	f.write(str(eventsDic))
	f.close()


class myServer(BaseHTTPRequestHandler):
	

	def getData(self, searchWords):
		global eventsDic
		relevantData = {}
		if searchWords != "":
			for event in eventsDic:
				for attrib in eventsDic[event]:
					if searchWords in eventsDic[event][attrib]:
						relevantData[event] = eventsDic[event]
		else:
			relevantData = eventsDic
		return relevantData

		
	def do_GET(self):
		if ( self.path[:5] == "/data" ):
			self.sendAsJson(self.path[6:])
			return
		elif ( self.path[:6] == "/getid" ):
			self.sendIdAsJson(self.path[7:])
			return
		self.serveFile()

			
	def sendAsJson(self, searchWords):
			self.send_response(200)
			self.send_header('Content-type','application/json')
			self.end_headers()
			jsonOutput = json.dumps(self.getData(searchWords))
			self.wfile.write(jsonOutput)

	def sendIdAsJson(self, id):
			self.send_response(200)
			self.send_header('Content-type','application/json')
			self.end_headers()
			jsonOutput = json.dumps(eventsDic[int(id)])
			self.wfile.write(jsonOutput)

	
	def serveFile(self):
		if self.path=="/":
			self.path="/index.html"

		try:
			sendReply = False

			# if the requested path has one of the known file extensions, set the mime type 
			#   of the response.
			matchingExtensions = [ x for x in mimetypes if self.path.endswith(x) ]
			if matchingExtensions:
				extension = matchingExtensions[0]
				mimetype = mimetypes[extension]
				sendReply = True

			if sendReply == True:
				#Open the static file requested and send it
				f = open(os.curdir + os.sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	
	def do_POST(self):
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
	                 'CONTENT_TYPE':self.headers['Content-Type'],
		})

		if self.path=="/post":

			formData = { key : form[key].value for key in form }
			if len(eventsDic.keys()) > 0:
				id = int(eventsDic.keys()[-1]) + 1
			else:
				id = 1
			eventsDic[id] = formData
			saveState()
			return

		if self.path=="/remove":
			formData = { key : form[key].value for key in form }
			eventsDic.pop(int(formData["id"]))
			saveState()
			return
			

		if self.path[:5]=="/edit":
			formData = { key : form[key].value for key in form }
			eventsDic[int(self.path[6:])] = formData
			saveState()
			return
		

		if self.path =="/openDir":
			subprocess.Popen('explorer "' + FILES_FOLDER + str(form["id"]) + '"')
			saveState()
			return
			
			
try:
	server = HTTPServer(('', PORT_NUMBER), myServer)
	print ('server started')
	server.serve_forever()
except KeyboardInterrupt:
	print ('shutting down the web server')
	server.socket.close()
	
