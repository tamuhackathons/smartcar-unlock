import smartcar
from flask import Flask, redirect, request, jsonify

app = Flask(__name__)


access = None

client = smartcar.AuthClient(
    client_id="7f76ba71-1fdc-4bc3-92e9-51c7f3304a41",
    client_secret="e1fddb8c-d5cb-4a2a-a9aa-12958b3bc73e",
    redirect_uri="http://localhost:8000/exchange",
    scope=['read_vehicle_info', "control_security", 
           "control_security:unlock", "control_security:lock", 
           "read_location", "read_odometer", "read_vin"],
    test_mode=True,
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
    
    access = client.exchange_code(code)
    
    return redirect(f"vehicle/{0}")

@app.route('/vehicle/<vid>/', methods=['GET'])
def vehicle(vid):
    global access
    
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    print(vehicle_ids)
    
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    
    info = vehicle.info()
    
    print(info)
    
    return jsonify(info)

@app.route('/vehicle/<vid>/unlock')
def unlock(vid):
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    vehicle.unlock()
    
    return redirect(f"vehicle/{vid}")

@app.route('/vehicle/<vid>/lock')
def lock(vid):
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    vehicle.unlock()
    
    return redirect(f"vehicle/{vid}")

@app.route('/vehicle/<vid>/locate')
def locate(vid):
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    
    vehicle = smartcar.Vehicle(vehicle_ids[int(vid)], access['access_token'])
    
    location_data = vehicle.location()
    
    return jsonify(location_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port="8000")
