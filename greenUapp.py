from pickle import FALSE
from re import A
import string
import random
from flask import Flask, redirect, request, render_template
from authentication import authenticated, get_account_type, getUser, userauthenticated, companyauthenticated
import sqlite3 as sql

app = Flask(__name__)

def render(name, **extra):
	return render_template(name+'.html', currentPage=name, user=getUser(request), **extra)


@app.route("/") 
def index():
	return render('index')

###############* Iniciar Sessao + Registo de Utilizador/Empresa *###############

@app.route('/iniciarSessao')
def iniciarSessao():
	return render('iniciarSessao')

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
	return redirect('/')


#############*  Parcerias Sustentaveis *############

@app.route('/parceriasSustentaveis')
#@authenticated
# , currentPage='parceriasSustentaveis', user=getUser(request)
def parceriasSust():
	return render('parceriasSustentaveis') 

@app.route('/formulario_parcerias')
@authenticated
def formulario_parcerias():
	return render_template('formulario_parcerias.html', currentPage='formulario_parcerias', user=getUser(request)) 


#############* Sobre Nos *############
@app.route('/sobreNos')
def sobreNos():
	return render('sobreNos')

#############* Conta Utilizador *############
@app.route('/userinfo')
@userauthenticated
def userinfo():
	return render('userinfo')

#############* Conta Empresa *############
@app.route('/companyinfo')
@companyauthenticated
def companyinfo():
	return render('companyinfo')

#############* Contactos *############
@app.route('/contactos')	
def contactos():
	return render('contactos')


#############* Alojamentos *#############

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

	return render_template('alojamentos.html', currentPage='alojamentos' ,lista=lista_alojamentos, user=getUser(request)) 


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

	return render_template('moreInfo.html',id=item,name=name,img=img,price=price, rating=rating, description=description, user=getUser(request) )


## Preço por noite do alojamento que se pretende reservar 
@app.route('/pagamentoAloj/<item>')
def pagamentoAloj(item):
	db = sql.connect("greenDB.db")
	result = db.execute("SELECT price FROM alojamentos WHERE ID_alojamento="+item+";")
	data = result.fetchall()
	db.close()

	price = data[0]

	return render_template('pagamentoAloj.html', price=price, currentPage='pagamentoAloj', user=getUser(request))

app.run(port=8080, debug=True)