import os
import socket
import json
import requests
import pygeohash as pgh
from influxdb import InfluxDBClient


HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 7007        # Port to listen on (non-privileged ports are > 1023)

apikey   = os.getenv("API_KEY")
influxHost   = os.getenv("INFLUX_HOST")
influxPort   = os.getenv("INFLUX_PORT")
influxDatabase   = os.getenv("INFLUX_DB")

def main():
    # message format 
    #{"username":"ubuntu","ip":"84.69.34.206","port":"51510"}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        client = InfluxDBClient(host=influxHost, port=influxPort, database=influxDatabase)
        client.create_database(influxDatabase)
        print(f'Connected to InfluxDB on {influxHost}:{influxPort} (v{client.ping()})')
        
        print(f'Listenning on {HOST}:{PORT}...')
        while True:
            conn, addr = s.accept()
            print('Client connected from {}{}'.format(addr[0], addr[1]))
                    
            while True:
                data = conn.recv(4096)
                print(f'\t> Data of type {type(data)} received: {data}')

                try:
                    d = json.loads(data.decode('UTF-8'))#.replace("'", '"'))
                except:
                    print('\t> [ERROR] Data is not json decodable! Disconnecting client...')
                    disconnect(conn)
                    break

                # Replace values **NO MATCH** by None
                for k in d:
                    if d[k] == '**NO MATCH**':
                        d[k] = None

                # Abort if there is no IP
                if not d['ip']:
                    print(f'\t> [ERROR] IP is None, so I will discard this measure')
                else:
                    # Get geohash
                    try:
                        req = requests.get('http://api.ipstack.com/{ip}?access_key={apikey}'.format(ip=d['ip'], apikey=apikey))
                        if req.status_code == 200:
                            info = req.json()
                            geohash = pgh.encode(info['latitude'], info['longitude'])
                            print(f'\t> Got info from IPstack')
                    except:
                        print(f'\t> [ERROR] Something occurred while getting IP information. Status code is {req.status_code}')
                        info = None
                        geohash = None
                    
                    measure = [
                                {
                                    "measurement": "failed_logins",
                                    "tags": {
                                        "geohash": geohash,
                                        "latitude": info['latitude'] if info else None,
                                        "longitude": info['longitude'] if info else None,
                                        "username": d['username'],
                                        "port": d['port'],
                                        "ip": d['ip'],
                                        "country_flag_emoji_unicode": info['location']['country_flag_emoji_unicode'] if info else None,
                                        "calling_code": info['location']['calling_code'] if info else None,
                                        "is_eu": info['location']['is_eu'] if info else None,
                                        "type": info['type'] if info else None,
                                        "continent_code": info['continent_code'] if info else None,
                                        "continent_name": info['continent_name'] if info else None,
                                        "region_code": info['region_code'] if info else None,
                                        "region_name": info['region_name'] if info else None,
                                        "city": info['city'] if info else None,
                                        "zip": info['zip'] if info else None
                                    },
                                    "fields": {
                                        "value": 1
                                    }
                                }
                            ]

                    client.write_points(measure)
                    print(f'\t> Point successfully stored: {measure}')


def disconnect(conn):
    conn.close()
    print('\t> Client disconnected')


if __name__ == '__main__':
    main()
