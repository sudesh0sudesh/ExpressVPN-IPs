# blocklist_generator.py
import csv
from datetime import datetime, timedelta

def generate_blocklist(csv_file='express_ips.csv', output_file='custom_blocklist.txt'):
    recent_ips = []
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    # Read CSV and filter IPs seen in last 24 hours
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            last_seen = datetime.strptime(row['Last Seen'], '%Y-%m-%d %H:%M:%S')
            if last_seen > cutoff_time:
                recent_ips.append(row['IP'])
    
    # Convert IPs to CIDR notation (/32 for single IPs)
    subnets = [f"{ip}/32" for ip in recent_ips]
    
    # Write subnets to blocklist file
    with open(output_file, 'w') as f:
        f.write('\n'.join(subnets))
    
    return len(subnets)

if __name__ == '__main__':
    num_blocked = generate_blocklist()
    print(f"Generated blocklist with {num_blocked} IPs")