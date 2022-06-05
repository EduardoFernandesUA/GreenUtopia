from flask import Flask
from flask import request
from flask import render_template
import sqlite3 as sql 

app = Flask(__name__)


@app.route("/") 
def index():
	return render_template('index.html')


@app.route('/iniciarSessao')
def iniciarSessao():
	return render_template('iniciarSessao.html')

@app.route('/parceriasSustentaveis')
def parceriasSust():
	return render_template('parceriasSustentaveis.html') 


@app.route('/sobreNos')
def sobreNos():
	return render_template('sobreNos.html')


@app.route("/alojamentos") 
def alojamentos():
	db = sql.connect("greenDB.db")
	result = db.execute("SELECT ID_alojamento,name,img_path FROM alojamentos;")
	rows = result.fetchall()
	db.close()

	lista_alojamentos=[]
	for row in rows:
		id=row[0]
		name=row[1]
		img=row[2].split("%")
		lista_alojamentos.append([id,name,img[0]])

	return render_template('alojamentos.html',lista=lista_alojamentos)

@app.route('/<item>')
def alojamentos_item(item):

	if item=="all":
		return alojamentos()

	db = sql.connect("greenDB.db")
	result = db.execute("SELECT ID_alojamento ,name,img_path FROM alojamentos;")
	rows = result.fetchall()
	db.close()

	lista_alojamentos=[]
	for row in rows:
		name=row[1]
		if item in name.lower(): 
			id=row[0]
			img=row[2].split("%")
			lista_alojamentos.append([id,name,img[0]])

	return render_template('alojamentos.html',lista=lista_alojamentos)

@app.route('/search', methods=['GET']) 
def alojamentos_search():
	
	item = request.args.get('search_name', '')	## To access parameters submitted in the URL (?key=value)
	query = item.split(";")

	rows=[]
	db = sql.connect("greenDB.db")

	item = query[0].replace("%'", "").lower()	

	result = db.execute("SELECT ID_alojamento, name, img_path FROM alojamentos WHERE name LIKE '%"+item+"%';")
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
			lista_alojamentos.append([id,name,img[0]])

	return render_template('alojamentos.html',lista=lista_alojamentos)


@app.route('/moreInfo/<item>')
def moreInfo_item(item):
	db = sql.connect("greenDB.db")
	result = db.execute("SELECT * FROM alojamentos WHERE ID_alojamento="+item+";")
	data = result.fetchall()
	db.close()

	name=data[0][1]
	img=data[0][2].split("%")
	price=data[0][3]  
	description=data[0][4]
	rating=data[0][5]

	return render_template('moreInfo.html',id=item,name=name,img=img,price=price,description=description, rating=rating )


app.run(debug=True)