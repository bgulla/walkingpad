from flask import Flask, request
from ph4_walkingpad import pad
from ph4_walkingpad.pad import WalkingPad, Controller
from ph4_walkingpad.utils import setup_logging
import asyncio
import yaml
import psycopg2
from datetime import date

app = Flask(__name__)

log = setup_logging()
pad.logger = log
ctler = Controller()

last_status = None


class WalkingPadData:
    def __init__(self, steps, distance, time):
        self.steps = steps

        # Distance in km
        self.distance = distance

        # Time in seconds
        self.time = time


def on_new_status(sender, record):

    distance_in_km = record.dist / 100
    print("Received Record:")
    print('Distance: {0}km'.format(distance_in_km))
    print('Time: {0} seconds'.format(record.time))
    print('Steps: {0}'.format(record.steps))

    last_status = WalkingPadData(record.steps, distance_in_km, record.time)

    #print("Storing in DB...")
    #store_in_db(record.steps, distance_in_km, record.time)


def store_in_db(steps, distance_in_km, duration_in_seconds):
    try:
        db_config = load_config()['database']
        conn = psycopg2.connect(host=db_config['host'], port=db_config['port'],
                                dbname=db_config['dbname'], user=db_config['user'], password=db_config['password'])
        cur = conn.cursor()

        date_today = date.today().strftime("%Y-%m-%d")
        duration = int(duration_in_seconds / 60)

        cur.execute("INSERT INTO exercise VALUES ('{0}', {1}, {2}, {3})".format(
            date_today, steps, duration, distance_in_km))
        conn.commit()

    finally:
        cur.close()
        conn.close()


def load_config():
    with open("config.yaml", 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def save_config(config):
    with open('config.yaml', 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


async def connect():
    address = load_config()['address']
    print("Connecting to {0}".format(address))
    await ctler.run(address)
    await asyncio.sleep(1.0)


async def disconnect():
    await ctler.disconnect()
    await asyncio.sleep(1.0)


@app.route("/config/address", methods=['GET'])
def get_config_address():
    config = load_config()
    return str(config['address']), 200


@app.route("/config/address", methods=['POST'])
def set_config_address():
    address = request.args.get('address')
    config = load_config()
    config['address'] = address
    save_config(config)

    return get_config_address()


@app.route("/mode", methods=['POST'])
async def change_pad_mode():
    new_mode = request.args.get('new_mode')
    print("Got mode {0}".format(new_mode))

    if (new_mode.lower() == "standby"):
        pad_mode = WalkingPad.MODE_STANDBY
    elif (new_mode.lower() == "manual"):
        pad_mode = WalkingPad.MODE_MANUAL
    else:
        return "Mode {0} not supported".format(new_mode), 400

    try:
        await connect()

        await ctler.switch_mode(pad_mode)
        await asyncio.sleep(1.0)
    finally:
        await disconnect()
    
    return new_mode


@app.route("/history", methods=['GET'])
async def get():
    try:
        await connect()

        await ctler.ask_hist(0)
        await asyncio.sleep(1.0)
    finally:
        await disconnect()

    return last_status, 200


ctler.handler_last_status = on_new_status

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5678)