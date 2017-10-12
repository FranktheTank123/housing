import requests
import yaml
import urllib
import xmltodict

ZILLOW_GET_SEARCH_RESULT = "http://www.zillow.com/webservice/GetSearchResults.htm"
ZILLOW_GET_ZESTIMATE = "http://www.zillow.com/webservice/GetZestimate.htm"

def get_zws():
	try:
		with open("config/zws.yaml", 'r') as f:
			tmp_ = yaml.load(f)
			return tmp_['ZWS_ID']
	except:
		return raw_input("Cannot locate ZWS. Please type your ZWS_ID: ")



def get_zpid(address, citystatezip="Seattle, WA 98104", ZWS_ID=""):
	f = {"address": address, "citystatezip": citystatezip, "zws-id": ZWS_ID}
	r = requests.get(ZILLOW_GET_SEARCH_RESULT + "?" + urllib.urlencode(f))
	dic = xmltodict.parse(r.content)
	try:
		return dic['SearchResults:searchresults']['response']['results']['result'][0]['zpid']
	except:
		return dic['SearchResults:searchresults']['response']['results']['result']['zpid']

def get_zestimate(zpid, ZWS_ID):
	f = {"zpid": zpid, "zws-id": ZWS_ID, "rentzestimate": True}
	r = requests.get(ZILLOW_GET_ZESTIMATE + "?" + urllib.urlencode(f))
	dic = xmltodict.parse(r.content)

	zvaluation = int(dic['Zestimate:zestimate']['response']['zestimate']['amount']['#text'])
	zvaluation_low = int(dic['Zestimate:zestimate']['response']['zestimate']['valuationRange']['low']['#text'])
	zvaluation_high = int(dic['Zestimate:zestimate']['response']['zestimate']['valuationRange']['high']['#text'])
	res = {
		"zvaluation": {
			"mean": zvaluation,
		 	"range": [zvaluation_low, zvaluation_high]
		 	}
	}
	try:
		rentzestimate = int(dic['Zestimate:zestimate']['response']['rentzestimate']['amount']['#text'])
		rentzestimate_low = int(dic['Zestimate:zestimate']['response']['rentzestimate']['valuationRange']['low']['#text'])
		rentzestimate_high = int(dic['Zestimate:zestimate']['response']['rentzestimate']['valuationRange']['high']['#text'])
		res.update({
			"rentzestimate": {
			"mean": rentzestimate,
			"range": [rentzestimate_low, rentzestimate_high]
			}	
		})
	except:
		print("No rent estimation found!")

	return res

def main():
	ZWS_ID = get_zws()

	address = raw_input("Address: ")
	city = raw_input("City, State: [Seattle, WA]") or "Seattle, WA "
	zipcode = raw_input("zip: [OPTIONAL]")
	zpid = get_zpid(address=address, citystatezip=" ".join([city, zipcode]), ZWS_ID=ZWS_ID)
	print get_zestimate(zpid, ZWS_ID=ZWS_ID)


if __name__ == '__main__':
	main()