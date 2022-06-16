import sqlite3 as sql

def authenticated(request):
	if not request.cookies.get('login_cookie'):
		# print("not authenticated")
		return False
	db = sql.connect('greenDB.db')
	result = db.execute( "SELECT cookie FROM login where email = '{}';".format(request.cookies.get('email')) ).fetchall()
	db.close()
	return request.cookies.get('login_cookie') == result[0][0]

def get_account_type(request): # user ou company
	db = sql.connect('greenDB.db')
	result = db.execute("SELECT type FROM login where email = '{}';".format(request.cookies.get('email')) ).fetchall()
	return result[0][0]

def getUser(request):
	if( authenticated(request)==False ):
		return []
	db = sql.connect('greenDB.db')
	result = db.execute("SELECT username, email, numero from login where email='{}';".format(request.cookies.get('email')) ).fetchall()
	print(result)
	return result[0]