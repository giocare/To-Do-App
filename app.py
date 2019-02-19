from flask import Flask, render_template, request, make_response, redirect, url_for
import os
import json
import requests

app = Flask(__name__)


@app.route('/')
def home():
	with open('./person.json') as f:
	  data = json.load(f)
	print('hello world')
	return render_template('index.html', langs=data["languages"])

# @app.route('/todos', methods=['post', 'get'])
# def todolist():
#     if request.method == 'POST':
#         newtask = request.form.get('task')  # 
#  	print(newtask)

#  	with open('./data.json') as f:
# 		file = json.load(f)
 
#     return render_template('todo.html', file=file)

@app.route('/register',methods=['post', 'get'])
def register():
	global uname
	if request.method == 'POST':
		uname = request.form.get('potentialusername')
		name = {"username": uname}  
		r = requests.post('https://hunter-todo-api.herokuapp.com/user', json=name)
		
		if r.status_code == 409:
			message = 'That username is taken. Try Again'
			return render_template('register.html', error=message)
		else:
			r = requests.post('https://hunter-todo-api.herokuapp.com/auth', json={"username": uname})
			cooki = json.loads(r.text)
			global cookies
			cookies = {"sillyauth": cooki['token']}
			r = requests.post('https://hunter-todo-api.herokuapp.com/auth', cookies=cookies, json={"username": uname})
			return redirect(url_for('todolist'))

	return render_template('register.html')



@app.route('/login', methods=['post', 'get'])
def login():
	if request.method == 'POST':
		global uname
		uname = request.form['username']

		r = requests.post('https://hunter-todo-api.herokuapp.com/auth', json={"username": uname})
		cooki = json.loads(r.text)

		global cookies
		cookies = {"sillyauth": cooki['token']}
		r = requests.post('https://hunter-todo-api.herokuapp.com/auth', cookies=cookies, json={"username": uname})
		return redirect(url_for('todolist'))

	return render_template('login.html')

@app.route('/todos', methods=['post', 'get'])
def todolist():
	global cookies
	global uname
	t = requests.get('https://hunter-todo-api.herokuapp.com/todo-item', cookies=cookies)
	file = json.loads(t.text)

	if request.method == 'POST':
		newtask = request.form.get('task') 
		print(newtask)
		response = requests.post('https://hunter-todo-api.herokuapp.com/todo-item', cookies=cookies, json={"content": newtask})
		t = requests.get('https://hunter-todo-api.herokuapp.com/todo-item', cookies=cookies)
		file = json.loads(t.text)
	

	return render_template('todo.html', name=uname, file=file)

@app.route('/update/<id>')
def updateitem(id):
	global cookies
	response = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/'+id, cookies=cookies, data = '{"completed":true}')
	return redirect(url_for('todolist'))

@app.route('/delete/<id>')
def deleteitem(id):
	response = requests.delete('https://hunter-todo-api.herokuapp.com/todo-item/'+id, cookies=cookies)
	return redirect(url_for('todolist'))

@app.route('/logout')
def logout():
	global uname
	uname = {""}
	global cookies
	cookies = {""}
	print('You have been logged out.')
	return redirect(url_for('register'))

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, threaded=True, debug=True)