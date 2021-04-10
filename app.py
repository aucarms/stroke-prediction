from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, login
from sqlalchemy.orm import Session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, event
from pycaret.regression import*
import pandas as  pd
import pickle
import numpy as np

#Get the current datetime
now = datetime.now()
#Load machine learning model and its columns
model = load_model('random_forest_model_final')
cols = ['gender', 'age', 'hypertension', 'heart_disease', 'ever_married', 'work_type', 'Residence_type', 'avg_glucose_level', 'bmi', 'smoking_status']

#Initialize app 
app = Flask(__name__)
app.secret_key = 'fluffyun1corn'
app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://postgres:postgres@localhost/usersignon")
# app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://rrzkdbhssysetl:1dc36b6def1b62ce514f603f1fb5761db857a961db6c5f8df92c3caf483050de@ec2-23-21-229-200.compute-1.amazonaws.com:5432/d323i38grcstf1")
app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://d323i38grcstf1/rrzkdbhssysetl@Heroku/d323i38grcstf1")
app.config["SQLALchemy_TRACK_MODIFICATIONS"] = False

db.init_app(app) 
login.init_app(app)
login.login_view= 'login'

#create database
@app.before_first_request
def create_table():
	db.create_all()
	print("database created successfully!")

#define login page path
@app.route('/home')
@login_required
def loadHome():
	return render_template('home.html')


#Login handler and defines the functions
@app.route('/login', methods=['POST', 'GET'])
#This method validates the username and pw
def login():
	if current_user.is_authenticated:
		return redirect('/home')
	
	if request.method == 'POST':
		username = request.form['username']
		pswd = request.form['password']
		user = User.query.filter_by(username = username).first()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		if user is not None and user.check_password(pswd):
			f = open("login_activity.txt", "a")
			f.write(username + "--Login Attempt:" + dt_string + "--Success\n")	
			f.close()
			login_user(user)
			return redirect('/home')
		f = open("login_activity.txt", "a")
		f.write(username + "--Login Attempt:" + dt_string + "--Failed\n")	
		f.close()
	return render_template('index.html')

#define the register page path and functions
@app.route('/register', methods=['POST','GET'])
#This method creates a new user in the database
def register():
	if current_user.is_authenticated:
		return redirect('/home')

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if User.query.filter_by(username=username).first():
			return('Username already exists.')
		hashed_pwd=generate_password_hash(str(password))
		user = User(username=username, password=hashed_pwd)
		deletemepass = str(password)
		db.session.add(user)
		db.session.commit()
		db.session.refresh(user)
		return redirect('/login')
	return render_template('register.html')
	
#Defines the logout page path and logsout the user
@app.route('/logout')
def logout():
	logout_user()
	return redirect('/login')

#Defines the homepage and functions 
@app.route('/home', methods=['POST'])
#This method utilizes the machine learning model to make predictions
def predict():
	#put all the form values in to a list
	features = [float(i) for i in request.form.values()]
	# Convert features to array
	array_features = [np.array(features)]
	# Predict features
	prediction = model.predict(array_features)
	output = prediction

	# Check the output values and retrieve the result with html tag based on the value
	if output == 1:
		return render_template('home.html', 
		result = 'The patient is not likely to have a stroke!')

	else:
		return render_template('home.html', 
		result = 'The patient is likely to have a stroke!')

	