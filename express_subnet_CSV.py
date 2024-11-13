import csv
import os
import requests
import datetime
import logging

INPUT_FILE = 'express_subnet.txt'
IP_GUIDE_URL = "https://ip.guide/"
OUTPUT_FILE = 'express_subnet.csv'

def read_txt(file_path) -> list:
    if os.path.exists(file_path):
        with open(file_path) as f:
            return f.read().splitlines()
    return []

def read_csv(file_path) -> list:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return list(csv.reader(f))
    return []

def fetch_asn(subnet):
    try:
        response = requests.get(f"{IP_GUIDE_URL}{subnet}")
        if response.status_code == 200:
            data = response.json().get('autonomous_system', {})
        elif response.status_code == 404:
            ip = subnet.split('/')[0]
            response = requests.get(f"{IP_GUIDE_URL}{ip}")
            data = response.json().get('network', {}).get('autonomous_system', {})
        else:
            raise ValueError(f"Received status code {response.status_code}")

        asn = data.get('asn', None)
        asn_org = data.get('organization', None)
        country = data.get('country', None)
        first_seen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_seen = first_seen

        if not asn:
            raise ValueError("Invalid response format")

        logging.info(f"Subnet: {subnet}, country: {country}")
    except Exception as e:
        print(f"Error fetching ASN {e} {subnet}")
        return None, None, None, None, None

    return asn, asn_org, country, first_seen, last_seen

def write_csv(file_path, data, header=None):
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(data)

def main():
    subnets = read_txt(INPUT_FILE)
    if not subnets:
        print(f"The file '{INPUT_FILE}' does not exist.")
        return

    output = []
    for subnet in subnets:
        asn, asn_org, country, first_seen, last_seen = fetch_asn(subnet)
        if asn:
            output.append([subnet, asn, asn_org, country, first_seen, last_seen])

    old_output = read_csv(OUTPUT_FILE)

    if not old_output:
        write_csv(OUTPUT_FILE, output, header=["Subnet", "ASN", "ASN Organization", "Country", "First Seen", "Last Seen"])
    else:
        old_output_dict = {row[0]: row for row in old_output}
        for row in output:
            if row[0] in old_output_dict:
                old_output_dict[row[0]][5] = row[5]  # Update last seen
            else:
                old_output_dict[row[0]] = row  # Add new entry

        updated_output = list(old_output_dict.values())
        write_csv(OUTPUT_FILE, updated_output)

if __name__ == '__main__':
    main()
