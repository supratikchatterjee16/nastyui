from http.server import HTTPServer, BaseHTTPRequestHandler
import pymongo
import json
import urllib

d = {}  #final dictionary
db_connect = pymongo.MongoClient('localhost', 27017)
database_name = 'nasty'
database = db_connect[database_name]
collections = database.collection_names(include_system_collections=False)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
	global d, database, collections
	def do_GET(self):
		path = self.path
		#print(path)
		if path == "/":
			path = "index.html"
		else:
			path = path[1:]
		self.send_response(200)
		self.end_headers()
		with open(path,"rb") as response:
			self.wfile.write(response.read())
	
	def generate_info(self,name):
		string = ""
		if name in collections:
			record = database[name]
			cursor = record.find({})
			string = 'Relations : ' + str(d[name]) + "\n\n"
			for doc in cursor:
				string = string + doc['title']+'\n'+doc['date']+'\n'+doc['link']+'\n\n'
		else:
			string = "not found"
		return string
	def do_POST(self):
		path = self.path
		post_methods = {"info":self.generate_info}
		length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(length).decode('utf-8')
		print(post_data)
		self.send_response(200)
		self.end_headers()
		self.wfile.write(post_methods[path[1:]](post_data).encode('utf-8'))


for collection in collections:
	record1 = database[collection]
	cursor = record1.find({})
	all_rels = []
	for doc in cursor:
		all_rels.append(doc['relations'])
	try:
		d[collection] = list(set(d[collect]+all_rels))
	except:
		d[collection] = all_rels

with open("relations.json","w+") as relfile:
	json.dump(d, relfile)

httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
print('Server started at 8000')
httpd.serve_forever()
