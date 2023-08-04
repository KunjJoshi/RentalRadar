import requests
import json
import time
from mortgage import amortization_schedule
import pandas as pd

API_KEY = "f8afd74a7dmsh8feb825ecf24206p1f7ef5jsnb0b19e15db3b"
HOST = "realty-mole-property-api.p.rapidapi.com"
US_HOST = "us-real-estate.p.rapidapi.com"
US_RE_HOST = "us-real-estate-listings.p.rapidapi.com"
property_data = []
rental_data=[]
research_params = {
  "location" : 'San Francisco, CA',
  "down_payment": 20.0,
  "interest_rate": 5.0, 
  "property_tax" : 1.2,
  "expense_ratio" : 0
}

def send_request(endpoint, params):
    url = f"https://{HOST}/{endpoint}"

    headers = {
        "content-type": "application/octet-stream",
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": HOST,
    }

    response = requests.get(url, headers=headers, params=params)
    return response

def get_property_records(address):
    endpoint = "properties"
    params = {"address": address}
    return send_request(endpoint, params)

def get_property_sale_price(address):
    endpoint = "salePrice"
    params = {"address": address}
    return send_request(endpoint, params)

def get_property_rental_price(address):
    endpoint = "rentalPrice"
    params = {"address": address}
    return send_request(endpoint, params)

def get_property_listings(zipcode):
    endpoint = "saleListings"
    params = {"zipCode":zipcode, "propertyType":"Single Family", "limit":"10"}
    response = send_request(endpoint, params)
    data = json.loads(response.content.decode('utf-8'))
    return data['data']['home_search']['results']

def get_property_for_sale_by_location(location):
    endpoint = "for-sale"
    params = {"location":location,"offset":"0","limit":"50", "property_type":"single_family"}
    url = f"https://{US_RE_HOST}/{endpoint}"
    headers = {
      "content-type": "application/octet-stream",
    	"X-RapidAPI-Key": API_KEY,
    	"X-RapidAPI-Host": US_RE_HOST
    }
    response = requests.get(url, headers=headers, params=params)
  
    #print (response.content)
    return json.loads(response.content.decode('utf-8'))

def get_property_for_sale(zipcode):
    endpoint = "v2/for-sale-by-zipcode"
    params = {"zipcode":zipcode,"offset":"0","limit":"42", "property_type":"single_family"}
    url = f"https://{US_HOST}/{endpoint}"
    headers = {
      "content-type": "application/octet-stream",
    	"X-RapidAPI-Key": API_KEY,
    	"X-RapidAPI-Host": US_HOST
    }
    response = requests.get(url, headers=headers, params=params)
    #print(response.content)
    return json.loads(response.content.decode('utf-8'))

def get_rental_market_data(zipcode):
   endpoint=f"zipCodes/{zipcode}"
   params={}
   response=send_request(endpoint=endpoint,params=params)
   #print(response)
   return response.json()

def calculate_rent_adjustment(bedrooms,sqft,baths,delta_rent):
  if(int(bedrooms) == 1):
      delta_sqft = delta_rent*0.8/700
      rent_adj = (sqft - 700) * delta_sqft
      rent_adj += (baths - 1) * (delta_rent * 0.2)
  elif(int(bedrooms) == 2): 
      delta_sqft = delta_rent*8/700
      rent_adj = (sqft - 1400) * delta_sqft
      rent_adj += (baths - 2) * (delta_rent * 0.2)
  elif(int(bedrooms) == 3): 
      delta_sqft = delta_rent*0.8/600
      rent_adj = (sqft - 2000) * delta_sqft
      rent_adj += (baths - 2) * (delta_rent * 0.2)
  elif(int(bedrooms) == 4): 
      delta_sqft = delta_rent*0.7/500
      rent_adj = (sqft - 2500) * delta_sqft
      rent_adj += (baths - 2) * (delta_rent * 0.3)
  elif(int(bedrooms) > 4): 
      delta_sqft = delta_rent*0.7/900
      rent_adj = (sqft - 3400) * delta_sqft
      rent_adj += (baths - 4) * (delta_rent * 0.15)
      rent_adj += (bedrooms - 5) * (delta_rent * 0.35)
    #print (f"Adjusted rent: {rent_adj} {delta_rent} {bedrooms} {baths} {sqft}")  
  return round(rent_adj, 2)

def derive_rental_estimate(address,bedroom,baths,sqft,rental_list):
   #print(bedroom)
   rent_estimate=0
   idx=0
   static_idx=0
   delta_rent=0
   for i in rental_list:
      idx=idx+1
      if (int(i['bedrooms'])==int(bedroom)):
         break
   idx=idx-1
   if(int(bedroom) == 1):
    delta_rent = rental_list[idx+1]['averageRent'] - rental_list[idx]['averageRent']
   elif(int(bedroom) > 4):
    delta_rent = rental_list[idx]['averageRent'] - rental_list[idx-1]['averageRent']
   else:
    delta_rent1 = rental_list[idx]['averageRent'] - rental_list[idx-1]['averageRent']
    delta_rent2 = rental_list[idx+1]['averageRent'] - rental_list[idx]['averageRent']
    delta_rent = (delta_rent1 + delta_rent2)/2
   #print(delta_rent)
   rent_estimate = rental_list[idx]['averageRent']
   rent_estimate += round(calculate_rent_adjustment(int(bedroom), int(sqft),int(baths), float(delta_rent))) 
   #print (f"{address} {idx} {delta_rent} {rent_estimate}")
   return rent_estimate 
      
  
def get_rental_estimate(address, bedrooms, baths, sqft):
    #print('In Rental Estimate Now')
    url = "https://realty-mole-property-api.p.rapidapi.com/rentalPrice"
    querystring = {
        "address": address,
        "propertyType": "Single Family",
        "bedrooms": bedrooms,
        "bathrooms": baths,
        "squareFootage": sqft,
        "compCount": "5"
    }
    headers = {
        "X-RapidAPI-Key": "f8afd74a7dmsh8feb825ecf24206p1f7ef5jsnb0b19e15db3b",
        "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    dic=response.json()
    #print(dic['rent'])
    return dic['rent']
      
def get_address_line(address, city, state_code, postal_code):
    address_line = "{}, {}, {}, {}".format(address, city, state_code, postal_code)
    return address_line

def generate_rental_potentials(zipcode):
  rental_list=[]
  listings = get_property_for_sale(zipcode)
  #print (listings)
  if(listings['status'] == 'OK'): 
    results = listings['data']['home_search']['results']
  else:
    listings = get_property_for_sale_by_location(zipcode)
    #print(listings)
    results = listings['listings']
    #print(listings['message'])
    #exit(listings['status'])
  rdata=get_rental_market_data(zipcode)
  for rental in rdata['rentalData']['detailed']:
     decoded_rent={
        'bedrooms':rental['bedrooms'],
        'averageRent':rental['averageRent'],
        'minRent':rental['minRent'],
        'maxRent':rental['maxRent'],
        'totalRentals':rental['totalRentals']
     }
     rental_list.append(decoded_rent)
  #print(rental_list)
  return rental_list,results

def collect_research_params(zipcode,downpayment,interest,propertytax,expense):
    exp_ratio = float(expense)
    down_pmt = float(downpayment)
    irate = float(interest)
    property_tax = float(propertytax) 
    research={}
    research["location"] = zipcode
    research["down_payment"] = down_pmt
    research["interest_rate"] = irate
    research["property_tax"] = property_tax
    research["expense_ratio"] = exp_ratio
    return research
def get_positive_cf(cflist):
   for i in range(len(cflist)):
      if cflist[i]>0:
         return i+1
   return len(cflist)

def get_positive_rroi(rroilist):
   for i in range(len(rroilist)):
      if rroilist[i]>0:
         return i+1
   return len(rroilist)
def analyze_property( incr_exp, incr_inc, incr_val,prop_data):
  yearly_exp = []
  yearly_inc = []
  yearly_val = []
  yearly_roi = []
  yearly_rroi = []
  yearly_iroi = []
  yearly_cf = []
  pdata = []
  yearly_texp = 0
  exp_mult = 1
  inc_mult = 1
  amt_tab = prop_data['amortization_schedule']
  home_val = prop_data['list_price']
  prop_tax = prop_data['property_tax']
  monthly_exp = prop_data['monthly_exp']
  invest_amount = prop_data['invest_amount']   
  
  for index, row in amt_tab.iterrows():
    year = int(index/12)
    if(index%12 == 0):
      if (year!=0):
        exp_mult = float(exp_mult) + (float(incr_exp)/100)
        inc_mult = float(inc_mult) + (float(incr_inc)/100)
        yearly_val.append(yearly_val[year-1] * (1+float(incr_val)/100))
        
      else:
        exp_mult = 1
        inc_mult = 1
        yearly_val.append(prop_data['list_price'])
      yearly_texp = 0
      yearly_exp.append(0)
      yearly_inc.append(0)
      yearly_cf.append(0)
      yearly_roi.append(yearly_val[year]-home_val)  
      yearly_rroi.append(round((yearly_inc[year-1]-yearly_exp[year-1])*100/invest_amount, 2))
      if(year == 0):
        yearly_iroi.append(0)
      else:  
        yearly_iroi.append(round((yearly_roi[year]*100/invest_amount)/year, 2))
    monthly_prop_tax = (prop_tax/12)*(yearly_val[year-1]/100)
    yearly_exp[year] = monthly_exp*exp_mult + monthly_prop_tax + row['interest'] + yearly_exp[year]
    yearly_inc[year] = row['total_inc']*inc_mult + yearly_inc[year]
    yearly_texp += row['principal']   
    yearly_cf[year] = yearly_inc[year] - (yearly_exp[year] + yearly_texp)
    if(index%12 == 11):
      #print(f"Year {year}: Expenses: {round(yearly_exp[year], 2)}, Income: {round(yearly_inc[year], 2)}, CF: {round(yearly_cf[year], 2)}, Value: {round(yearly_val[year], 2)}, ROI: {round(yearly_roi[year], 2)} rROI: {yearly_rroi[year]}% iROI: {yearly_iroi[year]}%")
      pdata.append ({
        "Year": year,
        "Expenses": round(yearly_exp[year],2),
        "Income": round(yearly_inc[year],2),
        "Cash Flow": round(yearly_cf[year],2),
        "Rental ROI": round(yearly_rroi[year],2),
        "Property Value": round(yearly_val[year],2),
        "Yearly ROI": round(yearly_roi[year],2),
        "Investment ROI": round(yearly_iroi[year],2)
      })
    #total_exp = row['total_exp']
    #total_inc = row['total_inc']
    #print (f"{index}: {total_exp:.2f} {total_inc:.2f}")
  #print (property_data[int(prop_id)]['amortization_schedule'])
  #print (pdata)
  pdf = pd.DataFrame(pdata)
  #print (pdf)
  return pdf
    


def collect_property_data(research,incr_exp,incr_val,incr_inc):
  index = 0
  #print(research)
  property_data=[]
  #print(research_params)
  location = research['location']
  #location = input("Enter Location (zipcode/city) for research: ")
  rent_list,results = generate_rental_potentials(location)
  #print(results)
  down_payment = research['down_payment']
  int_rate = research['interest_rate']
  
  
  for listing in results:
      address = listing['location']['address']['line']
      city = listing['location']['address']['city']
      state_code = listing['location']['address']['state_code']
      postal_code = listing['location']['address']['postal_code']
      if(postal_code == None): 
        postal_code = "00000"
      sqft = listing['description']['sqft']
      if(sqft == None):
        sqft = 0
      beds = listing['description']['beds']
      if(beds == None):
        beds = 0
      baths_full = listing['description']['baths_full']
      if(baths_full == None):
        baths_full = 0
      property_type = listing['description']['type']
      if(property_type == None):
        property_type = "Single Family"
      list_price = listing['list_price']
      if(list_price == None):
          list_price = 0
      desc=listing['description']['text']
      if desc==None:
         desc=''
      img_url=listing['primary_photo']['href']
      if img_url==None:
         img_url='https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Image_not_available.png/640px-Image_not_available.png'
      address_line = get_address_line(address, city, state_code, postal_code)
      #print(f"List price: {list_price}, Down payment: {down_payment}, Interest rate: {int_rate}")
      loan_amount = list_price - (list_price*down_payment/100)
      invest_amount=list_price*down_payment/100
      loan_term = 30
      address_line = get_address_line(address, city, state_code, postal_code)
      #rental_estimate = get_rental_estimate(address_line, beds, baths_full, sqft)
      rental_estimate=derive_rental_estimate(address_line,beds,baths_full,sqft,rent_list)
      #print(rental_estimate)
      if(rental_estimate == None):
          rental_estimate = 0
      
      #Property Analysis
      amt_tab = amortization_schedule(int_rate, loan_amount, loan_term)
      prop_tax = research['property_tax']
      monthly_prop_tax = ((prop_tax/12)*list_price)/100
      monthly_exp = research['expense_ratio']
      amt_tab['total_exp'] = amt_tab['interest'] + monthly_exp + monthly_prop_tax
      amt_tab['total_inc'] = rental_estimate
      amt_tab['total_pnl'] = amt_tab['total_inc'] - amt_tab['total_exp'] 
      #print (".", end="")
      prop_data={
          "index": index,
          "address": address,
          "address_line": address_line,
          "sqft": int(sqft),
          "beds": int(beds),
          "baths_full": int(baths_full),
          "type": property_type,
          "list_price": round(float(list_price), 2),
          "rent_estimate": round(float(rental_estimate), 2),
          'amortization_schedule':amt_tab,
          "property_tax": prop_tax,
          "monthly_exp": monthly_exp,
          'description':desc,
          'invest_amount':invest_amount,
          'image_url':img_url
      }
      pData=analyze_property(incr_exp,incr_inc,incr_val,prop_data)
      print(pData)
      prop_data['years']=list(pData['Year'])
      prop_data['expenses']=list(pData['Expenses'])
      prop_data['income']=list(pData['Income'])
      prop_data['cflow']=list(pData['Cash Flow'])
      prop_data['rroi']=list(pData['Rental ROI'])
      prop_data['pval']=list(pData['Property Value'])
      prop_data['yroi']=list(pData['Yearly ROI'])
      prop_data['iroi']=list(pData['Investment ROI'])
      cpos=get_positive_cf(prop_data['cflow'])
      prop_data['cflow_positive']=cpos
      rpos=get_positive_rroi(prop_data['rroi'])
      prop_data['rroi_positive']=rpos

      property_data.append(prop_data)

      index += 1
  #print(property_data)
  return property_data

def conv_str_to_lst(string):
   noofspaces=string.count(' ')
   for i in range(noofspaces):
      string=string.replace(' ','')
   noofbrackets=string.count('[')
   for i in range(noofbrackets):
      string=string.replace('[','')
   noofbrackets=string.count(']')
   for i in range(noofbrackets):
      string=string.replace(']','')
   newlist=string.split(',')
   for i in range(len(newlist)):
      newlist[i]=float(newlist[i])
   #print(len(newlist))
   return newlist




