import requests
import json

API_KEY = "f8afd74a7dmsh8feb825ecf24206p1f7ef5jsnb0b19e15db3b"
HOST = "realty-mole-property-api.p.rapidapi.com"
US_HOST = "us-real-estate.p.rapidapi.com"

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

def get_property_for_sale(zipcode):
    endpoint = "v2/for-sale-by-zipcode"
    params = {"zipcode":zipcode,"offset":"0","limit":"100", "property_type":"single_family"}
    url = f"https://{US_HOST}/{endpoint}"
    headers = {
        "content-type": "application/octet-stream",
    	"X-RapidAPI-Key": API_KEY,
    	"X-RapidAPI-Host": US_HOST
    }
    response = requests.get(url, headers=headers, params=params)
    return json.loads(response.content.decode('utf-8'))

zipcode = input("Please enter zipCode for analysis: ")

listings = get_property_for_sale(zipcode)
results = (listings['data']['home_search']['results'])

print("Listing Details:")
print(f"{'Address':<32} {'SqFt':<8} {'Price':<10} {'#Beds':<6} {'#Baths':<6}")
for listing in results:
    address = listing['location']['address']['line']
    sqft = listing['description']['sqft']
    price = listing['list_price']
    beds = listing['description']['beds']
    baths = listing['description']['baths']
    #print(f"{address:<32} {sqft:<8} ${price:<10} {beds:<6} {baths:<6}")
  