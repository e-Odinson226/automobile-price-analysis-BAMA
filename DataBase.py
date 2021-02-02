import mysql.connector
import sklearn.tree as tree
from sklearn.preprocessing import LabelEncoder

try:
    database = mysql.connector.connect( user = "/",
                                        password = "/",
                                        host = "127.0.0.1",
                                        database = "cars"    )
    cursor = database.cursor()
    cursor.execute("SELECT * FROM cars")
    data = cursor.fetchall()
except:
    raise Exception("DataBase error")

try:
    listed_data = []
    for instance in data:
        listed_data.append([instance[0],instance[3], instance[2], instance[1]])
except:
    raise Exception("Data formation error")

try:
    x = []
    y = []
    encoded_models = {}
    models = []
    for raw_data in listed_data:
        x.append(raw_data[0:3])
        y.append(raw_data[3])
        models.append(raw_data[0])
except:
    raise Exception("Error while Creating list of data")

try:
    label_encoder = LabelEncoder()
    label_encoder.fit(models)
    labeled_models = label_encoder.transform(models)
    for i in range(0, len(x)):
    #    print(x[i][0], labeled_models[i])
        encoded_models[x[i][0]] = labeled_models[i]
        x[i][0] = labeled_models[i]
    key = True
    while key:
        car_name = input("Car name:")
        car_model = int(input("Model:"))
        car_mileage = int(input("Mileage:"))
        
        if encoded_models.__contains__(car_name):
            clf = tree.DecisionTreeClassifier()
            clf = clf.fit(x, y)
            sample = [encoded_models[car_name], car_model, car_mileage]
            pr = clf.predict([sample])
            print(label_encoder.inverse_transform([sample[0]])," --> ", pr)
            key = False
        else:
            print("[", car_name, "] is not defined, Try again.")
except:
    raise Exception("AI error")