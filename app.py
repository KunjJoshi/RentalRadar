from flask import Flask, render_template, request
from main import get_property_for_sale,collect_research_params,collect_property_data,conv_str_to_lst
import webbrowser
from io import StringIO
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')


@app.route('/listings', methods=['POST'])
def listings():
  zipcode = request.form['zipcode']
  print(zipcode)
  downpayment=request.form['downpayment']
  interest=request.form['interest']
  propertytax=request.form['propertytax']
  expense=request.form['expense']

  research=collect_research_params(zipcode,downpayment,interest,propertytax,expense)
  results=collect_property_data(research=research)
  return render_template('listings.html',result=results)

@app.route('/parameters',methods=['POST'])
def parameters():
  zipcode=request.form['zipcode']
  return render_template('parameters.html',zip=zipcode)

@app.route('/analyse',methods=['POST'])
def analyse():
  prd=request.form['period']
  period=conv_str_to_lst(prd)
  interest=conv_str_to_lst(request.form['interest'])
  principal=conv_str_to_lst(request.form['principal'])
  monthly_payment=conv_str_to_lst(request.form['monthly_payment'])
  outstanding_balance=conv_str_to_lst(request.form['outstanding_balance'])
  total_interest=conv_str_to_lst(request.form['total_interest'])
  property={}
  property['beds']=request.form['beds']
  property['baths']=request.form['baths']
  property['protax']=request.form['protax']
  property['rent']=request.form['rent']
  property['address']=request.form['address']
  property['list_price']=request.form['list_price']
  property['sqft']=request.form['sqft']
  property['description']=request.form['description']
  property['image']=request.form['image']
  property['amortized_over']='30 years'
  property['period']=period
  property['interest']=interest
  property['principal']=principal
  property['monthly_payment']=monthly_payment
  property['total_interest']=total_interest
  property['outstanding_balance']=outstanding_balance
  return render_template('analysed.html',properties=property)

@app.route('/about-us')
def aboutus():
  return render_template('aboutus.html')

@app.route('/contact-us')
def contactus():
  return render_template('contactus.html')

@app.route('/mission')
def mission():
  return render_template('mission.html')

@app.route('/subscribe')
def subscribe():
  return render_template('subscribe.html')

@app.route('/send-email',methods=['POST'])
def sendemail():
  name=request.form['name']
  email=request.form['email']
  enquiry=request.form['enquiry']
  return render_template('index.html')

if __name__ == '__main__':
  app.run(host='127.0.0.1',port='5000',debug=True)

webbrowser.open('http://127.0.0.1:5000')
