import smartcar, configparser
from flask import Flask, redirect, request, jsonify, render_template

config = configparser.ConfigParser()
config.read('config.ini')

AuthConfig = config["Auth"]
HOST = config["Config"]["host"]
PORT = config["Config"]["port"]
DEBUG = config["Config"]["debug"]

app = Flask(__name__)

access = None
vehicle_ids = None

client = smartcar.AuthClient(
    client_id=AuthConfig["client_id"],
    client_secret=AuthConfig["client_secret"],
    redirect_uri=AuthConfig["redirect_url"],
    scope=['read_vehicle_info', "control_security", 
           "control_security:unlock", "control_security:lock", 
           "read_location", "read_odometer", "read_vin"],
    test_mode=AuthConfig["test_mode"],
)
    
def merge_dicts(dict1, dict2, dict3):
    return {**dict1, **dict2, **dict3}

@app.route('/')
def home():
    if vehicle_ids:
        return redirect('index')
    elif request.args.get('code'):
        code = request.args.get('code')
        exchange_dialog(code)
        
        return '<script src="https://javascript-sdk.smartcar.com/redirect-2.0.0.js"></script>'
    else:
        return redirect('login')

@app.route('/index')
def index():
    vehicles = {}
    
    for vid in vehicle_ids:
        vehicle = smartcar.Vehicle(vid, access['access_token'])
        info = vehicle.info()
        
        if info['make'] not in vehicles.keys():
            vehicles[info['make']] = []
        
        location = vehicle.location()
        odom = vehicle.odometer()
        
        vehicles[info['make']].append([merge_dicts(location, odom, info)])
    
    return render_template('index.html', cars = vehicles, login='false')

@app.route('/login', methods=['GET'])
def login():
    auth_url = client.get_auth_url()
    return render_template('index.html', cid=str(AuthConfig["client_id"]),
                           uri=str(AuthConfig['redirect_url']),
                           port=PORT, login='true')

@app.route('/waiting')
def waiting():
    while not vehicle_ids:
        pass
    
    return redirect("index")

def exchange_dialog(code):
    global access
    global vehicle_ids
    
    access = client.exchange_code(code)
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']

@app.route('/exchange', methods=['GET'])
def exchange():
    global access
    global vehicle_ids
    
    code = request.args.get('code')
    
    access = client.exchange_code(code)
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    return redirect("index")

@app.route('/vehicle/<vid>/', methods=['GET'])
def vehicle(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    
    return jsonify(vehicle.info())

@app.route('/vehicle/<vid>/unlock')
def unlock(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    vehicle.unlock()
    
    return redirect(f"vehicle/{vid}")

@app.route('/vehicle/<vid>/lock')
def lock(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    vehicle.lock()
    
    return redirect(f"vehicle/{vid}")

@app.route('/vehicle/<vid>/locate')
def locate(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    
    return jsonify(vehicle.location())

@app.route('/vehicle/<vid>/vin')
def vin(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access["access_token"])
    
    return jsonify(vehicle.vin())

@app.route('/vehicle/<vid>/odometer')
def odometer(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access["access_token"])
    
    return jsonify(vehicle.odometer())

@app.route('/refreshtoken')
def refreshtoken():
    if smartcar.expired(access["expiration"]):
        access = client.exchange_refresh_token(access["refresh_token"])
    
    return redirect(f"vehicle/0")

@app.route('/user')
def user():
    return jsonify(smartcar.get_user_id())

if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
