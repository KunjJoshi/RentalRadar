from flask import Flask, render_template, request
from main import get_property_for_sale,collect_research_params,collect_property_data,conv_str_to_lst,analyze_property,get_positive_cf,get_positive_rroi
import webbrowser
from io import StringIO
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/index',methods=['GET'])
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
  incr_exp=request.form['incr_exp']
  incr_inc=request.form['incr_inc']
  incr_val=request.form['incr_val']
  research=collect_research_params(zipcode,downpayment,interest,propertytax,expense)
  results=collect_property_data(research,incr_exp,incr_val,incr_inc)
  return render_template('listings.html',result=results)

@app.route('/parameters',methods=['POST'])
def parameters():
  zipcode=request.form['zipcode']
  return render_template('parameters.html',zip=zipcode)

@app.route('/analyse',methods=['POST'])
def analyse():
  property={}
  property['id']=request.form['id']
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
  property['invest_amount']=request.form['invest_amount']
  property['monthly_exp']=request.form['monthly_exp']
  property['years']=conv_str_to_lst(request.form['years'])[1:]
  property['expenses']=conv_str_to_lst(request.form['expenses'])[1:]
  property['income']=conv_str_to_lst(request.form['income'])[1:]
  property['cflow']=conv_str_to_lst(request.form['cflow'])[1:]
  property['iroi']=conv_str_to_lst(request.form['iroi'])[1:]
  property['rroi']=conv_str_to_lst(request.form['rroi'])[1:]
  property['yroi']=conv_str_to_lst(request.form['yroi'])[1:]
  property['pval']=conv_str_to_lst(request.form['pval'])[1:]
  cash_flow_positive=get_positive_cf(property['cflow'])
  property['cflowpos']=cash_flow_positive
  roi_pos=get_positive_rroi(property['rroi'])
  property['rroipos']=roi_pos
  #print('Interest',property['iroi'])
  #print('Yearly',property['yroi'])
  #print('Rental',property['rroi'])
  #print(property)
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
  app.run(host='0.0.0.0',port='5000',debug=True)

webbrowser.open('http://127.0.0.1:5000')
