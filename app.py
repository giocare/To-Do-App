from flask import Flask, render_template, request, make_response, redirect, url_for
import os
import json
import requests

app = Flask(__name__)

#This function generates the register page
@app.route('/',methods=['post', 'get'])
def register():
	global uname
	#take the input and check if a user already exists
	if request.method == 'POST':
		uname = request.form.get('potentialusername')
		name = {"username": uname}  
		r = requests.post('https://hunter-todo-api.herokuapp.com/user', json=name)
		
		#if a user with the entered name exists, reload the page with an error message
		if r.status_code == 409:
			message = 'That username is taken. Try Again'
			return render_template('register.html', error=message)
			
		#create new user and redirect to to-do page
		else:
			r = requests.post('https://hunter-todo-api.herokuapp.com/auth', json={"username": uname})
			cooki = json.loads(r.text)
			global cookies
			cookies = {"sillyauth": cooki['token']}
			r = requests.post('https://hunter-todo-api.herokuapp.com/auth', cookies=cookies, json={"username": uname})
			return redirect(url_for('todolist'))

	return render_template('register.html')


#This function generates the login page
@app.route('/login', methods=['post', 'get'])
def login():
	#authenticate user and redirect to to-do page
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


#This function displays the todo list
@app.route('/todos', methods=['post', 'get'])
def todolist():
	global cookies
	global uname
	t = requests.get('https://hunter-todo-api.herokuapp.com/todo-item', cookies=cookies)
	file = json.loads(t.text)
	# when a new task is added-> do a post request then reload page with new to-do
	if request.method == 'POST':
		newtask = request.form.get('task') 
		response = requests.post('https://hunter-todo-api.herokuapp.com/todo-item', cookies=cookies, json={"content": newtask})
		t = requests.get('https://hunter-todo-api.herokuapp.com/todo-item', cookies=cookies)
		file = json.loads(t.text)
	
	return render_template('todo.html', name=uname, file=file)


#This function marks tasks as completed and not comleted
@app.route('/update/<id>/<status>')
def updateitem(id,status):
	global cookies
	#if current task is marked as false, mark as true
	if status == 'False':
		response = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/'+id, cookies=cookies, data = '{"completed":true}')
	#if current task is marked as true, mark as false
	if status == 'True':
		response = requests.put('https://hunter-todo-api.herokuapp.com/todo-item/'+id, cookies=cookies, data = '{"completed":false}')
	return redirect(url_for('todolist'))


#This function deletes tasks
@app.route('/delete/<id>')
def deleteitem(id):
	response = requests.delete('https://hunter-todo-api.herokuapp.com/todo-item/'+id, cookies=cookies)
	return redirect(url_for('todolist'))


#This function logs the user out
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