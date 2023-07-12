import requests
import json
import time
from mortgage import amortization_schedule

API_KEY = "f8afd74a7dmsh8feb825ecf24206p1f7ef5jsnb0b19e15db3b"
HOST = "realty-mole-property-api.p.rapidapi.com"
US_HOST = "us-real-estate.p.rapidapi.com"
US_RE_HOST = "us-real-estate-listings.p.rapidapi.com"
property_data = []
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

def get_rental_estimate(address, bedrooms, baths, sqft):
    print('In Rental Estimate Now')
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
    print(dic['rent'])
    return dic['rent']
      
def get_address_line(address, city, state_code, postal_code):
    address_line = "{}, {}, {}, {}".format(address, city, state_code, postal_code)
    return address_line

def generate_rental_potentials(zipcode):
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
  return results

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
  
def collect_property_data(research):
  index = 0
  print(research)
  #print(research_params)
  location = research['location']
  #location = input("Enter Location (zipcode/city) for research: ")
  results = generate_rental_potentials(location)
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
      address_line = get_address_line(address, city, state_code, postal_code)
      #print(f"List price: {list_price}, Down payment: {down_payment}, Interest rate: {int_rate}")
      loan_amount = list_price - (list_price%down_payment)
      loan_term = 30
      address_line = get_address_line(address, city, state_code, postal_code)
      rental_estimate = get_rental_estimate(address_line, beds, baths_full, sqft)
      if(rental_estimate == None):
          rental_estimate = 0
      
      #Property Analysis
      amt_tab = amortization_schedule(int_rate, loan_amount, loan_term)
      amt_tab_cols=amt_tab.columns
      print(amt_tab_cols)
      prop_tax = research['property_tax']
      monthly_prop_tax = ((prop_tax/12)*loan_amount)/100
      monthly_exp = research['expense_ratio']
      amt_tab['total_exp'] = amt_tab['interest'] + monthly_exp + monthly_prop_tax
      amt_tab['total_inc'] = rental_estimate
      amt_tab['total_pnl'] = amt_tab['total_inc'] - amt_tab['total_exp'] 
      period=list(amt_tab['period'])
      interest=list(amt_tab['interest'])
      principal=list(amt_tab['principal'])
      mo_pa=list(amt_tab['monthly_payment'])
      ou_ba=list(amt_tab['outstanding_balance'])
      to_in=list(amt_tab['total_interest'])
      
      time.sleep(1)
      #print (".", end="")
      property_data.append({
          "index": index,
          "address": address,
          "address_line": address_line,
          "sqft": int(sqft),
          "beds": int(beds),
          "baths_full": int(baths_full),
          "type": property_type,
          "list_price": round(float(list_price), 2),
          "rent_estimate": round(float(rental_estimate), 2),
          "period":period,
          "interest":interest,
          "principal":principal,
          "monthly_payment":mo_pa,
          "outstanding_balance":ou_ba,
          "total_interest":to_in,
          "property_tax": prop_tax,
          "monthly_exp": monthly_exp
      })
      index += 1
  #print(property_data)
  return property_data

#def generate_rental_report(prop_data):
  

def analyze_property(prop_id):
  #prop_data = property_data[int(prop_id)]
  print (property_data[int(prop_id)]['amortization_schedule'])
  
    
def print_rental_potentials():
  print("Listing Details:")
  print("{:<5} {:<24} {:<8} {:<6} {:<6} {:<10} {:<16}".format("Idx", "Address", "SqFt",
                                                        "# Beds",
                                                        "# Baths",
                                                        "Price",
                                                        "Rental Estimate"
                                                        ))
  for property in property_data:
    index = property['index']      
    address = property['address']
    sqft = property['sqft']
    beds = property['beds']
    baths_full = property['baths_full']
    list_price = property['list_price']
    rental_estimate = property['rent_estimate']
    print("{:<5} {:<24} {:<8} {:<6} {:<6} ${:<10} ${:<16}".format(index, address, sqft, beds, baths_full, list_price, rental_estimate))

#def conv_str_to_lst(string):
def plot_expense_vs_income(index):
  print(index, " Plot function is not ready yet!")
  
def print_main_menu():
  print("")
  print("Main Menu:")
  print("1. Collect Rental Research Parameters")
  print("2. Collect Rental Potentials based on city")
  print("3. Analyze Property from Potential list")
  print("4. Plot Expense vs. Income for Selected Property")
  print("5. Exit")
  option = input("Enter the operation you like to perform: ")
  return option

def main_function():
  option = print_main_menu()
  while (option != '5'):
    if(option == '3'):
      index = input("Enter the index of the property to analyze: ")
      analyze_property(int(index))
    elif(option == '4'):  
      index = input("Enter the index of the property to plot: ")
      plot_expense_vs_income(int(index))
    elif(option == '2'):
      collect_property_data()
      print_rental_potentials()
    elif(option == '1'):
      collect_research_params()
      print (research_params)
    option = print_main_menu()
  
#main_function()

#input_loan = 500000
#input_years = 30

#scenario1 = amortization_schedule(4.00, input_loan, input_years)
#scenario2 = amortization_schedule(3.00, input_loan, input_years)
#scenario3 = amortization_schedule(2.00, input_loan, input_years)

#print (scenario1)
