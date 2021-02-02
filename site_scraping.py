import mysql.connector
from bs4 import BeautifulSoup
import re
import requests
import numpy
from price_parser import Price
from persiantools.jdatetime import JalaliDate
#--------Define CAR as a class-----------------------------
class Car:
    counter = 0
    def __init__(self, name, model, price, mileage):
        self.name = name
        self.model = model
        self.price = price
        self.mileage = mileage
        Car.counter += 1
    
    def get_name(self):
        return(str(self.name).strip())
    def get_model(self):
        return(str(self.model).strip())
    def get_price(self):
        return(str(self.price).strip())
    def get_mileage(self):
        return(str(self.mileage).strip())

#--------Define Functions----------------------------------
def situation(car):
    overview = car.find('div', attrs={"class" : "overview"})
    p = overview.find("p", attrs={"class" : "cost"})
        
    if p.find("span", attrs={"itemprop" : "price", "class" : "", "style" : ""}):
        if (p.find("span", attrs={"itemprop" : "price", "style" : ""})).get("content"):
            return True

def price(car):
    overview = car.find('div', attrs={"class" : "overview"})
    p = overview.find("p", attrs={"class" : "cost"})
        
    if p.find("span", attrs={"itemprop" : "price", "style" : ""}):
            price = p.find("span", attrs={"itemprop" : "price", "style" : ""})
            price = price.get("content")
            return price
                

def name_model(car):
    link = car.find('a', attrs={'href': re.compile("^https://")}).get("href")
    
    web_page = requests.get(link)
    if(web_page.ok):
        html_data = BeautifulSoup(web_page.content, "html.parser")
        info = html_data.find("div", attrs={"class" : "prd-detail ad-detail-maindiv"})
        details = info.find("div", attrs={"class" : "inforight"})
        
        #----------Model / Name----------
        models_name = details.find("h1", attrs={"class" : "addetail-title"})
        models= models_name.find_all("span", attrs={})
        #----------Model-----------------
        model_year = models[-1].text
        model_year = int(re.search("\d+",model_year)[0])
        if model_year < 1450:
                model_year = JalaliDate(model_year,1,1).to_gregorian().year
        #----------Name------------------
        for i in range(0, len(models)-1):
            models[i] = models[i].text.strip()
        
        models = models[:-1]
        models = " ".join(models)
        models = models.split()
        
        for model in models:
            if "\u200f" == model:
                models.remove(model)
        
        models = " ".join(models)
        
        return  (models, model_year)

def mileage(car):
    list_data = car.find("div", attrs={"class" : "listdata"})
    details = list_data.find("div", attrs={"class" : "detail"})
    mid = details.find("div", attrs={"class" : "mid"})
    clearfix = mid.find("div", attrs={"class" : "clearfix web-milage-div"})
     
    
    if clearfix.find("p", attrs={"class" : "price milage-text-mobile visible-xs price-milage-mobile"}):
        mileage = clearfix.find("p", attrs={"class" : "price milage-text-mobile visible-xs price-milage-mobile"})
        mileage = mileage.text.strip()

        pattern = re.compile(r"([0-9]*[,][0-9]*)+")
        if pattern.search(mileage):
            mileage = (''.join(re.findall(r"(\d+)+", pattern.search(mileage)[0])))
            return(int(mileage))
        else:
            return(int("0"))
    else:
        return(int("0"))

#--------Define variables----------------------------------
page_counter = 10
links = []
cars = []
flag = False
#--------MIAN RUNNER---------------------------------------
pages = numpy.arange(1, page_counter, 1)
try:
    for page in pages:
        url = "https://bama.ir/car/all-brands/all-models/all-trims?page=" + str(page)
        web_page = requests.get(url)

        try:
            if(web_page.ok):
                html_data = BeautifulSoup(web_page.content, "html.parser") 
                # ads_div is a part that car ads are stored on it, in web page.
                ads_div = html_data.find("div", attrs={"class" : "eventlist car-ad-list-new clearfix"})
                # Now we get a object of soup, called (cars) wich contains a list of car ads.
                carss = ads_div.find_all("li", attrs={"class" : "car-list-item-li"})
                # Start a loop to catch every ad's link.
                for car in carss:
                    # Filter the part that contains the link.
                    if situation(car):
                        automobile = Car(   name_model(car)[0],
                                            name_model(car)[1],
                                            price(car),
                                            mileage(car)   )
                        cars.append(automobile)
                        
                        
            else:
                raise Exception
        except:
            raise Exception
except:
    raise Exception
#--------Write data to DataBase----------------------------
try:
    database = mysql.connector.connect( user = "/",
                                        password = "/",
                                        host = "127.0.0.1",
                                        database = "cars"   )
    curser = database.cursor()
    
    #--------Define DataBase-----------------------------------
    curser.execute("SELECT * FROM cars")
    cars_db = curser.fetchall()

    if cars_db:
        try:
            for car in cars:
                flag = False
                for stored_car in cars_db:
                    if stored_car[0] == car.get_name() and stored_car[1] == car.get_price() and stored_car[2] == car.get_model() and stored_car[3] == car.get_mileage():
                        flag = True
                if flag == False:
                    curser.execute("INSERT INTO cars(Name, Price, Model, Mileage) VALUES(%s, %s, %s, %s)", (car.get_name(), car.get_price(), car.get_model(), car.get_mileage()))
                database.commit()                    
        except:
            raise Exception    
    if not cars_db:
        try:
            for car in cars:
                curser.execute("INSERT INTO cars(Name, Price, Model, Mileage) VALUES(%s, %s, %s, %s)", (car.get_name(), car.get_price(), car.get_model(), car.get_mileage()))
            database.commit()
        except:
            raise Exception("ERROR DATABASE WRITING")
            exit
except:
    raise Exception("ERROR DATABASE READING")
    exit