import asyncio
import websockets
import json
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.environ["clientId"]
client_secret = os.environ["clientSecret"]
headset_id = os.environ["headsetId"]
cortex_token = ''
message = {}

def get_cortex_info():
    global message
    message = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getCortexInfo"
    }

def check_login_info():
    global message
    message = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "getUserLogin"
    }

def check_user_access_rights():
    global message
    message = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "requestAccess",
        "params": {
            "clientId": client_id,
            "clientSecret": client_secret
        }
    }

def authorize():
    global message
    message = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "authorize",
        "params": {
            "clientId": client_id,
            "clientSecret": client_secret
        }
    }


def query_headsets():
    global message
    message = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "queryHeadsets"
    }

async def connect_to_cortex():
    uri = "wss://localhost:6868" 
    async with websockets.connect(uri) as websocket:

        while True:
            print("What do you want to do?: ")
            print("1. Get cortex info.")
            print("2. Check login info.")
            print("3. Check User Access info.")
            print("4. Authorize app and get cortex token.")
            print("5. See all connected headsets.")
            print("10. Exit")
            n = input("Enter choice: ")
            if n == '1':
                get_cortex_info()
            elif n == '2':
                check_login_info()
            elif n == '3':
                check_user_access_rights()
            elif n == '4':
                authorize()
            elif n == '5':
                query_headsets()
            elif n == '10':
                break
            await websocket.send(json.dumps(message))
            print(f"Sent: {message}")
            response = await websocket.recv()
            print(f"Received: {response}")

# Run the WebSocket client
asyncio.get_event_loop().run_until_complete(connect_to_cortex())
