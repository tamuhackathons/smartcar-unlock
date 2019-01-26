import smartcar, configparser
from flask import Flask, redirect, request, jsonify

config = configparser.ConfigParser()
config.read('config.ini')

AuthConfig = config["Auth"]

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

@app.route('/login', methods=['GET'])
def login():
    auth_url = client.get_auth_url()
    print(auth_url)
    return redirect(auth_url)


@app.route('/exchange', methods=['GET'])
def exchange():
    code = request.args.get('code')
    
    print(code)
    
    global access
    global vehicle_ids
    
    access = client.exchange_code(code)
    
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    return redirect(f"vehicle/{0}")

@app.route('/vehicle/<vid>/', methods=['GET'])
def vehicle(vid):
    global access
    
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    
    info = vehicle.info()
    
    return jsonify(info)

@app.route('/vehicle/<vid>/unlock')
def unlock(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    vehicle.unlock()
    
    return redirect(f"vehicle/{vid}")

@app.route('/vehicle/<vid>/lock')
def lock(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    vehicle.unlock()
    
    return redirect(f"vehicle/{vid}")

@app.route('/vehicle/<vid>/locate')
def locate(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    
    return jsonify(vehicle.location())

@app.route('/vehicle/<vid>/vin')
def vin(vid):
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access["access_token"])
    
    return jsonify(vehicle.vin())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="8000")
