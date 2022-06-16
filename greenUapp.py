import string
import random
from flask import Flask, redirect, request, render_template
import sqlite3 as sql

app = Flask(__name__)

def authenticated(request):
	if not request.cookies.get('login_cookie'):
		print("not authenticated")
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
	db = sql.connect('greenDB.db')
	result = db.execute("SELECT username, email, numero from login where email='{}';".format(request.cookies.get('email')) ).fetchall()
	return result[0]

@app.route("/") 
def index():
	return render_template('index.html', currentPage='inicio')

@app.route('/iniciarSessao')
def iniciarSessao():
	return render_template('iniciarSessao.html', currentPage='iniciarSessao')

@app.route('/dologin', methods=['POST'])
def login():
	email = request.form.get('email')
	password = request.form.get('password')
	if email is None or password is None:
		return redirect('/iniciarSessao?error=emptyfields')

	db = sql.connect("greenDB.db")
	result = db.execute("SELECT password,type FROM login where email = '{}';".format(email) ).fetchall()
	account_type = result[0][1]
	db.close()
	if len(result) == 0:
		return redirect('/iniciarSessao?error=noUser')

	print(result[0][0], password, result[0][0] == password)
	if result[0][0] == password:
		loginid = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 12))
		db = sql.connect("greenDB.db")
		db.execute("UPDATE login SET cookie = '{}' where email = '{}';".format(loginid, email))
		db.commit()
		db.close()
		resp = redirect('/userinfo') if account_type=="user" else redirect('/companyinfo')
		resp.set_cookie('login_cookie', loginid)
		resp.set_cookie('email', email)
		print(result)
		return resp
	return redirect('/iniciarSessao')
	
@app.route('/douserresgiter', methods=['POST'])
def user_register():
	username = request.form.get('username')
	email = request.form.get('email')
	password = request.form.get('password')
	password2 = request.form.get('password2')
	if username is None or email is None or password is None or password2 is None:
		return redirect('/iniciarSessao?error=emptyfields')
	if password != password2:
		return redirect('/iniciarSessao?error=diferentpasswords')

	cookie = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 12))

	db = sql.connect("greenDB.db")
	result = db.execute("SELECT * FROM login where email = '"+email+"';").fetchall()
	db.close()
	if len(result) != 0:
		return redirect('/iniciarSessao?error=alreadyExists')

	db = sql.connect('greenDB.db')
	db.execute("insert into login (username,password,email,numero,cookie,type) values ('{}','{}','{}','{}','{}','{}');".format(username, password, email, "", cookie, "user"))
	db.commit()
	db.close()
	resp = redirect('/userinfo') 
	resp.set_cookie('email', email)
	resp.set_cookie('login_cookie', cookie)
	return resp

@app.route('/docompanyresgiter', methods=['POST'])
def company_register():
	username = request.form.get('username')
	email = request.form.get('email')
	contact = request.form.get('contact')
	password = request.form.get('password')
	password2 = request.form.get('password2')
	if username is None or email is None or password is None or password2 is None:
		return redirect('/iniciarSessao?error=emptyfields')
	if password != password2:
		return redirect('/iniciarSessao?error=diferentpasswords')

	cookie = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 12))

	db = sql.connect("greenDB.db")
	result = db.execute("SELECT * FROM login where email = '"+email+"';").fetchall()
	db.close()
	if len(result) != 0:
		return redirect('/iniciarSessao?error=alreadyExists')

	db = sql.connect('greenDB.db')
	db.execute("insert into login (username,password,email,numero,cookie,type) values ('{}','{}','{}','{}','{}','{}');".format(username, password, email, contact, cookie, "company"))
	db.commit()
	db.close()
	resp = redirect('/companyinfo')
	resp.set_cookie('email', email)
	resp.set_cookie('login_cookie', cookie)
	return resp

@app.route('/logout')
def logout():
	db = sql.connect("greenDB.db")
	db.execute("UPDATE login SET cookie = '{}' where email = '{}';".format("logout", request.cookies.get('email')))
	db.commit()
	db.close()
	return redirect('/iniciarSessao')

@app.route('/parceriasSustentaveis')
def parceriasSust():
	return render_template('parceriasSustentaveis.html', currentPage='parceriasSustentaveis') 


@app.route('/sobreNos')
def sobreNos():
	return render_template('sobreNos.html', currentPage='sobreNos', user=getUser(request))

@app.route('/userinfo')
def userinfo():
	if not authenticated(request):
		return redirect("/iniciarSessao")
	user = getUser(request)
	print(user)
	if len(user[2])==0: 
		user = (user[0], user[1], "-")
	return render_template('userinfo.html', currentPage='userInfo', user=user)

# temp init
@app.route('/addcookie')
def setcookie():
	resp = redirect("/userinfo")
	resp.set_cookie('login_cookie', "cookie")
	return resp

@app.route('/removecookie')
def removecookie():
	resp = redirect("/userinfo")
	resp.set_cookie('login_cookie', "")
	return resp
	
# end temp

@app.route('/companyinfo')
def companyinfo():
	return render_template('companyinfo.html', currentPage='companyInfo')

@app.route('/contactos')	
def contactos():
	return render_template('contactos.html', currentPage='contactos')


@app.route("/alojamentos") 
def alojamentos():
	db = sql.connect("greenDB.db")
	result = db.execute("SELECT ID_alojamento,name,img_path, price, rating FROM alojamentos;")	
	rows = result.fetchall()
	db.close()

	lista_alojamentos=[]
	for row in rows:
		id=row[0]
		name=row[1]
		img=row[2].split("%")
		price = row[3]		
		rating = row[4]		
		lista_alojamentos.append([id,name,img[0], price, rating])	

	return render_template('alojamentos.html', currentPage='alojamentos' ,lista=lista_alojamentos) 

@app.route('/<item>')
def alojamentos_item(item):

	if item == "all":		
		return alojamentos()

	db = sql.connect("greenDB.db")
	result = db.execute("SELECT ID_alojamento ,name,img_path, price, rating FROM alojamentos;")	
	rows = result.fetchall()
	db.close()

	lista_alojamentos=[]
	for row in rows:
		name = row[1]
		if item in name.lower(): 
			id=row[0]
			img=row[2].split("%")
			price=row[3]		
			rating=row[4]		
			lista_alojamentos.append([id,name,img[0], price, rating])		

	return render_template('alojamentos.html',lista=lista_alojamentos)

@app.route('/search', methods=['GET']) 
def alojamentos_search():
	
	item = request.args.get('search_name', '')	## To access parameters submitted in the URL (?key=value)
	query = item.split(";")
	print(query)

	item2 = request.args.get('check_in', '')
	print(item2)

	rows=[]
	db = sql.connect("greenDB.db")

	item = query[0].replace("%'", "").lower()	

	result = db.execute("SELECT ID_alojamento, name, img_path, price, rating FROM alojamentos WHERE name LIKE '%"+item+"%';")
	rows = result.fetchall()

	if len(query)>1:
		for i in range(1,len(query)):
			db.execute(query[i])

	db.close()

	lista_alojamentos=[] # lista de tuplos

	for row in rows:      
		name=row[1]
		if item in name.lower(): 
			id=row[0]
			img=row[2].split("%")
			price=row[3]
			rating=row[4]
			lista_alojamentos.append([id,name,img[0], price, rating])

	return render_template('alojamentos.html', currentPage='search',lista=lista_alojamentos)


@app.route('/moreInfo/<item>')
def moreInfo_item(item):
	db = sql.connect("greenDB.db")
	result = db.execute("SELECT * FROM alojamentos WHERE ID_alojamento="+item+";")
	data = result.fetchall()
	db.close()

	name=data[0][1]
	img=data[0][2].split("%")
	price=data[0][3]  
	rating=data[0][4]
	description=data[0][5]

	return render_template('moreInfo.html',id=item,name=name,img=img,price=price, rating=rating, description=description )

###* Obter apenas o nome e o preço por noite 
#* do alojamento que se vai fazer a reserva
@app.route('/pagamentoAloj/<item>')
def pagamentoAloj(item):

	if not authenticated(request):
		return redirect("/iniciarSessao")

	db = sql.connect("greenDB.db")
	result = db.execute("SELECT price FROM alojamentos WHERE ID_alojamento="+item+";")
	data = result.fetchall()
	db.close()

	price = data[0]

	return render_template('pagamentoAloj.html', price=price)


app.run(debug=True)