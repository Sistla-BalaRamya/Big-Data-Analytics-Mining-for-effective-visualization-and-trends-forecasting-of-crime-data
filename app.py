#import of packages, Libraries and modules.
from flask import Flask,render_template, request, flash, url_for,jsonify
import pandas as pd
import numpy as np
from flask import json
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
import joblib
from sklearn.linear_model import BayesianRidge
from plotly.offline import init_notebook_mode, iplot
import sqlite3

#Starting of flask app
app = Flask(__name__)

@app.route("/")
def intro():
    return render_template("intro.html")

@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route('/login')
def login():
	return render_template('signin.html')

@app.route("/signup")
def signup():

    username = request.args.get('user','')
    name = request.args.get('name','')
    email = request.args.get('email','')
    number = request.args.get('mobile','')
    password = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `info` (`user`,`email`, `password`,`mobile`,`name`) VALUES (?, ?, ?, ?, ?)",(username,email,password,number,name))
    con.commit()
    con.close()
    return render_template("signin.html")

@app.route("/signin")
def signin():

    mail1 = request.args.get('user','')
    password1 = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `user`, `password` from info where `user` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signin.html")    

    elif mail1 == 'admin' and password1 == 'admin':
        return render_template("home.html")

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("home.html")
    else:
        return render_template("signup.html")

@app.route('/Index')
def Index():
	return render_template("home.html")

@app.route("/home.html")
def Home():
	return render_template("home.html")

@app.route('/pred.html')
def pred():
	return render_template("pred.html")

@app.route('/vis.html')
def viz():
	return render_template("vis.html")

@app.route('/womenViz.html')
def womenViz():	
	return render_template('womenViz.html')

@app.route('/childrenViz.html')
def childrenViz():	
	return render_template('childrenViz.html')

@app.route('/IPCViz.html')
def IPCViz():	
	return render_template('IPCViz.html')

@app.route('/highlights.html')
def highlights():
	return render_template("highlights.html")

@app.route('/women.html',methods = ['POST'])
def women():

	year = request.form.get("Predict_Year")		#Year fetching From UI.
	C_type = request.form.get("C_Type")			#Crime type fetching from UI
	state = request.form.get("state")			#State name fetching from UI
	
	df = pd.read_csv("dataset/StateWiseCAWPred.csv", header=None)

	data1 = df.loc[df[0]==state].values			#Selecting State and its attributes.
	for x in data1:
		if x[1] == C_type:
			test = x
			break


	l = len(df.columns)					
	trendChangingYear = 2	

	xTrain = np.array([1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021])
	yTrain = test[2:29]

	X = df.iloc[0,2:l].values
	y = test[2:]
	regressor = BayesianRidge(compute_score=True)	#regression algorithm cealled.
	regressor.fit(X.reshape(-1,1),y)	#Data set is fitted in regression and Reshaped it.
	accuracy = regressor.score(X.reshape(-1,1),y)	#Finding Accuracy of Predictions.
	accuracy_max = 0.65

	#Trending year(Influence Year) finding algorithm.
	if(accuracy < 0.65):			#Used 65% accuracy as benchmark for trending year finding algorithm.
		for a in range(3,l-8):

			X = df.iloc[0,a:l].values
			y = test[a:]
			regressor = BayesianRidge(compute_score=True)
			regressor.fit(X.reshape(-1,1),y)
			accuracy = regressor.score(X.reshape(-1,1),y)
			if (accuracy > accuracy_max):
				accuracy_max = accuracy
				trendChangingYear = a
	
	year = int(year)
	y = test[2:]
	b = []

	#If accuracy is Lower than 65%, only visualization of the data is shown - no predictions
	if accuracy < 0.65:				
		for k in range(2001,2020):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = "Data is not Sutaible for prediction"

	#Else predictions are shown and Run time data and labels are added to the graph.
	else:

		for j in range(2020,year+1):
			prediction = regressor.predict(np.array([[j]]))
			if(prediction < 0):
				prediction = 0
			y = np.append(y,prediction)
		y = np.append(y,0)

		for k in range(1990,year+1):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = ""
	if C_type == "ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY":
		C_type = "ASSAULT ON WOMEN"
	#Finally the template is rendered
	return render_template('women.html',data = [accuracy,yTrain,xTrain,state,year,data1,X,y,test,l],msg = msg,state=state, year=year, C_type=C_type,pred_data = y,years = yearLable)

@app.route('/children.html',methods = ['POST'])
def children():

	year = request.form.get("Predict_Year")		#Year fetching From UI.
	C_type = request.form.get("C_Type")			#Crime type fetching from UI
	state = request.form.get("state")			#State name fetching from UI

	#reading CSV file.
	df = pd.read_csv("dataset/Statewise Cases Reported of Crimes Committed Against Children.csv", header=None)

	data1 = df.loc[df[0]==state].values			#Selecting State and its attributes.
	for x in data1:
		if x[1] == C_type:
			test = x
			break


	l = len(df.columns)

	trendChangingYear = 2
	accuracy_max = 0.65

	# Year array for Javascript for Labeling to the Graph  
	xTrain = np.array([1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021])
	yTrain = test[2:25]

	X = df.iloc[0,2:l].values
	y = test[2:]
	regressor = BayesianRidge(compute_score=True)		#regression Algorithm Called.
	regressor.fit(X.reshape(-1,1),y)	#Data set is fitted in regression and Reshaped it.
	accuracy = regressor.score(X.reshape(-1,1),y)	#Finding Accuracy of Prdictions.
	
	accuracy_max = 0.65
	if(accuracy < 0.65):
		for a in range(3,l-4):

			X = df.iloc[0,a:l].values
			y = test[a:]
			regressor = BayesianRidge(compute_score=True)
			regressor.fit(X.reshape(-1,1),y)
			accuracy = regressor.score(X.reshape(-1,1),y)
			if (accuracy > accuracy_max):
				accuracy_max = accuracy
				
				trendChangingYear = a
	
	yTrain = test[trendChangingYear:]
	xTrain = xTrain[trendChangingYear-2:]
	regressor.fit(xTrain.reshape(-1,1),yTrain)
	accuracy = regressor.score(xTrain.reshape(-1,1),yTrain)

	year = int(year)
	y = test[2:]
	b = []
	if accuracy < 0.65:
		for k in range(2001,2021):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		year = 2016
		msg = "Data is not Suitable for prediction"
	else:

		for j in range(2020,year+1):
			prediction = regressor.predict(np.array([[j]]))
			if(prediction < 0):
				prediction = 0
			y = np.append(y,prediction)
		y = np.append(y,0)

		for k in range(1994,year+1):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = ""

	return render_template('children.html',data = [accuracy,yTrain,xTrain,state,year,data1,X,y,test,l],state=state, year=year,msg=msg, C_type=C_type,pred_data = y,years = yearLable)

@app.route('/ipc.html',methods = ['POST'])
def ipc():

	year = request.form.get("Predict_Year")		#Year fetching From UI.
	C_type = request.form.get("C_Type")			#Crime type fetching from UI
	state = request.form.get("state")			#State name fetching from UI

	#reading CSV file.
	df = pd.read_csv("dataset/StateIPCPred.csv", header=None)

	data1 = df.loc[df[0]==state].values			#Selecting State and its attributes.
	for x in data1:
		if x[1] == C_type:
			test = x
			break


	l = len(df.columns)
	trendChangingYear = 2
	accuracy_max = 0.65

	# Year array for Javascript for Labeling to Graph  
	xTrain = np.array([2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021])
	yTrain = test[2:18]

	X = df.iloc[0,2:l].values
	y = test[2:]
	regressor = BayesianRidge(compute_score=True)		#regression Algorithm Called.
	regressor.fit(X.reshape(-1,1),y)	#Data set is fitted in regression and Reshaped it.
	accuracy = regressor.score(X.reshape(-1,1),y)	#Finding Accuracy of Prdictions.

	
	accuracy_max = 0.65

	#Trending year(Influence Year) finding algorithm.
	if(accuracy < 0.65):			#Used 65% accuracy as benchmark for trending year finding algorithm.
		for a in range(3,l-4):

			X = df.iloc[0,a:l].values
			y = test[a:]
			regressor = BayesianRidge(compute_score=True)
			regressor.fit(X.reshape(-1,1),y)
			accuracy = regressor.score(X.reshape(-1,1),y)
			if (accuracy > accuracy_max):
				accuracy_max = accuracy
				
				trendChangingYear = a
	
	year = int(year)
	y = test[2:]
	b = []

	#If accuracy is Lower than 65%, only Visualization of the data is shown - no predictions.
	if accuracy < 0.65:
		for k in range(2006,2021):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		year = 2021
		msg = "Data is not Suitable for prediction"

	#Else predictions are shown and Run time data and labels are added to the graph.
	else:

		for j in range(2021,year+1):
			prediction = regressor.predict(np.array([[j]]))
			if(prediction < 0):
				prediction = 0
			y = np.append(y,prediction)
		y = np.append(y,0)

		for k in range(2001,year+1):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = ""
	
	#Finally the template is rendered.
	return render_template('ipc.html',data = [accuracy,yTrain,xTrain,state,year,data1,X,y,test,l],msg = msg, state=state, year=year, C_type=C_type,pred_data = y,years = yearLable)


@app.route('/sll.html',methods = ['POST'])
def sll():

	year = request.form.get("Predict_Year")		#Year fetching From UI.
	C_type = request.form.get("C_Type")			#Crime type fetching from UI
	state = request.form.get("state")			#State name fetching from UI

	#reading CSV file.
	df = pd.read_csv("dataset/StateSLLPred.csv", header=None)

	data1 = df.loc[df[0]==state].values			#Selecting State and its attributes.
	for x in data1:
		if x[1] == C_type:
			test = x
			break


	l = len(df.columns)
	trendChangingYear = 2
	accuracy_max = 0.65

	# Year array for Javascript for Labeling to Graph  
	xTrain = np.array([2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016])
	yTrain = test[2:18]

	X = df.iloc[0,2:l].values
	y = test[2:]
	regressor = BayesianRidge(compute_score=True)		#regression Algorithm Called.
	regressor.fit(X.reshape(-1,1),y)	#Data set is fitted in regression and Reshaped it.
	accuracy = regressor.score(X.reshape(-1,1),y)	#Finding Accuracy of Prdictions.
	
	accuracy_max = 0.65

	#Trending year(Influence Year) finding algorithm.
	if(accuracy < 0.65):			#Used 65% accuracy as benchmark for trending year finding algorithm.
		for a in range(3,l-4):

			X = df.iloc[0,a:l].values
			y = test[a:]
			regressor = BayesianRidge(compute_score=True)
			regressor.fit(X.reshape(-1,1),y)
			accuracy = regressor.score(X.reshape(-1,1),y)
			if (accuracy > accuracy_max):
				accuracy_max = accuracy
				
				trendChangingYear = a
	
	year = int(year)
	y = test[2:]
	b = []

	#If accuracy is Lower than 65%, only Visualization of the data is shown - not predictions.
	if accuracy < 0.65:
		for k in range(2001,2021):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		year = 2021
		msg = "Data is not Suitable for prediction"

	#Else predictions are shown and Run time data and labels are added to the graph.
	else:

		for j in range(2021,year+1):
			prediction = regressor.predict(np.array([[j]]))
			if(prediction < 0):
				prediction = 0
			y = np.append(y,prediction)
		y = np.append(y,0)

		for k in range(2001,year+1):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = ""
	
	#Finally the template is rendered.
	return render_template('sll.html',data = [accuracy,yTrain,xTrain,state,year,data1,X,y,test,l],msg = msg, state=state, year=year, C_type=C_type,pred_data = y,years = yearLable)


#routing Path for About page.
@app.route('/About.html')
def About():
	return render_template("/About.html")


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000, debug=True)

