#!/usr/bin/env python3
import subprocess
import socket
import concurrent.futures
import ipaddress
import platform
import sys

def ping_host(ip):
    """Vérifie si un hôte est accessible"""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-W', '1', str(ip)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def get_hostname(ip):
    """Récupère le nom d'hôte d'une IP"""
    try:
        hostname = socket.gethostbyaddr(str(ip))[0]
        return hostname
    except:
        return "N/A"

def scan_network(network_range):
    """Scanner le réseau et retourner les hôtes actifs"""
    print(f"Scan du réseau {network_range}...")
    network = ipaddress.ip_network(network_range, strict=False)
    active_hosts = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Créer les tâches de ping
        future_to_ip = {executor.submit(ping_host, ip): ip for ip in network.hosts()}
        
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                if future.result():
                    hostname = get_hostname(ip)
                    active_hosts.append({'ip': str(ip), 'hostname': hostname})
                    print(f"✓ {ip} - {hostname}")
            except Exception as e:
                print(f"Erreur pour {ip}: {e}")
    
    return active_hosts

def main():
    # Réseau à scanner (modifiez selon votre réseau)
    network_range = "172.17.240.0/24"  # Ajustez le masque selon votre réseau
    
    print("="*60)
    print("SCANNER RÉSEAU")
    print("="*60)
    
    active_hosts = scan_network(network_range)
    
    print("\n" + "="*60)
    print(f"RÉSUMÉ: {len(active_hosts)} équipements trouvés")
    print("="*60)
    
    for host in sorted(active_hosts, key=lambda x: ipaddress.ip_address(x['ip'])):
        print(f"IP: {host['ip']:<15} | Nom: {host['hostname']}")
    
    # Optionnel : sauvegarder dans un fichier
    with open('scan_results.txt', 'w') as f:
        f.write(f"Scan du {network_range}\n")
        f.write("="*60 + "\n")
        for host in sorted(active_hosts, key=lambda x: ipaddress.ip_address(x['ip'])):
            f.write(f"IP: {host['ip']:<15} | Nom: {host['hostname']}\n")
    
    print(f"\nRésultats sauvegardés dans 'scan_results.txt'")

if __name__ == "__main__":
    main()