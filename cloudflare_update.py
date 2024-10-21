import os, json, requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

cloudflare_api = "https://api.cloudflare.com/client/v4/"
cloudflare_zone_id = os.getenv("cloudflare_zone_id")
cloudflare_api_key = os.getenv("cloudflare_api_key")
subdomain = os.getenv("name")

current_ip = requests.get("https://ipinfo.io/ip").text.strip()

def log_output(action, data):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"{timestamp} - {action}: {json.dumps(data, indent=4)}\n"
    with open("cloudflare_dns_update.log", "a") as log_file:
        log_file.write(log_message)


headers = {
    "Authorization" : f"Bearer {cloudflare_api_key}",
    "Content-Type" : "application/json"
}

def get_dns_records():
    url = f"{cloudflare_api}zones/{cloudflare_zone_id}/dns_records"
    response = requests.get(url, headers=headers)
    with open("dns_records.json", "w") as f:
        f.write(json.dumps(response.json(), indent=4))
    return response.json()

def get_record_id(records):
    for record in records['result']:
        if record['name'] == subdomain:
            return record['id']
    return None


def update_dns_record(record_id, new_ip):
    url = f"{cloudflare_api}zones/{cloudflare_zone_id}/dns_records/{record_id}"
    data = {
        "type": "A",
        "name": subdomain,
        "content": new_ip,
        "ttl": 1,
        "proxied": False
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    log_output("Update DNS Record", response.json())


update_dns_record(get_record_id(get_dns_records()), current_ip)