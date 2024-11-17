import dns.resolver
import os
import requests
import csv
import datetime

DNS_SERVERS = ['1.1.1.1', '1.0.0.1']
DOMAIN_FILE = 'express.txt'
OUTPUT_FILE = 'express_subnet.txt'
MAIN_FILE = 'express_ips.csv'
NEW_IPS_FILE = 'new_express_ips.csv'
IP_GUIDE_URL = "https://ip.guide/"

def configure_dns_resolver():
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = DNS_SERVERS
    return resolver

def write_csv(file_path, header, data):
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

def read_existing_ips(file_path):
    exs_ip_data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                exs_ip_data[row['IP']] = {
                    'First Seen': row['First Seen'],
                    'Last Seen': row['Last Seen']
                }
    return exs_ip_data

def write_ips_to_file(ips, file_path):
    existing_data = read_existing_ips(file_path)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_ips=[]
    for ip in ips:
        if ip in existing_data:
            existing_data[ip]['Last Seen'] = current_time
        else:
            existing_data[ip] = {'First Seen': current_time, 'Last Seen': current_time}
            new_ips.append([ip, current_time, current_time])
            
    updated_data = [[ip, times['First Seen'], times['Last Seen']] for ip, times in existing_data.items()]
    write_csv(file_path, ["IP", "First Seen", "Last Seen"], updated_data)
    
    if new_ips:
        write_csv(NEW_IPS_FILE, ["IP", "First Seen", "Last Seen"], new_ips)
    

def read_domains_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"The file '{file_path}' does not exist.")
        exit(1)
    with open(file_path) as f:
        return [line.strip() for line in f]

def fetch_subnet_for_ip(ip):
    try:
        response = requests.get(f"{IP_GUIDE_URL}{ip}")
        if response.status_code == 200:
            subnet = response.json().get('network', {}).get('cidr', None)
            if not subnet:
                raise ValueError("Invalid response format")
        else:
            raise ValueError(f"Received status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching subnet for IP {ip}: {e}")
        ip_split = str(ip).split('.')
        subnet = f"{'.'.join(ip_split[:3])}.0/24"
    return subnet

def resolve_domains_to_subnets(domains, resolver):
    ip_out=set()
    ip_subnet = set()
    for domain in domains:
        print(f"Resolving domain: {domain}")
        try:
            temp_ips=set()
            for i in range(0,10):
                answers = resolver.resolve(domain, 'A')
                for ip in answers:
                    temp_ips.add(str(ip))
                    ip_out.add(str(ip))
            for ip in temp_ips:
                subnet = fetch_subnet_for_ip(ip)
                print(f"Subnet: {subnet}")
                ip_subnet.add(subnet)
        except Exception as e:
            print(f"Error resolving {domain}: {e}")
    return ip_subnet, ip_out

def write_subnets_to_file(subnets, file_path):
    with open(file_path, 'w') as f:
        for item in subnets:
            f.write(f"{item}\n")

def main():
    resolver = configure_dns_resolver()
    domains = read_domains_from_file(DOMAIN_FILE)
    subnets,ips = resolve_domains_to_subnets(domains, resolver)
    write_subnets_to_file(subnets, OUTPUT_FILE)
    write_ips_to_file(ips, MAIN_FILE)
    

if __name__ == "__main__":
    main()
