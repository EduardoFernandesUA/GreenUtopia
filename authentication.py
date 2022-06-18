import sqlite3 as sql
from flask import request

from flask import redirect

def private_authenticated():
	if not request.cookies.get('login_cookie'):
		# print("not authenticated")
		return False
	db = sql.connect('greenDB.db')
	result = db.execute( "SELECT cookie FROM login where email = '{}';".format(request.cookies.get('email')) ).fetchall()
	db.close()
	return request.cookies.get('login_cookie') == result[0][0]

def authenticated(function):
	def authenticated_function():
		if not private_authenticated():
			return redirect('iniciarSessao')
		else:
			return function()
	authenticated_function.__name__ = function.__name__
	return authenticated_function

def companyauthenticated(function):
	print("a")
	def authenticated_function():
		print("b", get_account_type())
		if not private_authenticated() or get_account_type()!='company' :
			print("asdf")
			return redirect('userinfo')
		else:
			return function()
	authenticated_function.__name__ = function.__name__
	return authenticated_function

def userauthenticated(function):
	def authenticated_function():
		if not private_authenticated() or get_account_type()!='user' :
			return redirect('companyinfo')
		else:
			return function()
	authenticated_function.__name__ = function.__name__
	return authenticated_function


def get_account_type(): # user ou company
	db = sql.connect('greenDB.db')
	result = db.execute("SELECT type FROM login where email = '{}';".format(request.cookies.get('email')) ).fetchall()
	return result[0][0]

def getUser(request):
	if not private_authenticated() :
		return []
	db = sql.connect('greenDB.db')
	result = db.execute("SELECT username, email, numero from login where email='{}';".format(request.cookies.get('email')) ).fetchall()
	if len(result[0][2])==0:
		result[0] = [*result[0]]
		result[0][2] = '.'
	print(result)
	return result[0]