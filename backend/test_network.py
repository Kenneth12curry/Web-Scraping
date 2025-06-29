#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes de connectivité réseau
"""

import requests
import socket
import dns.resolver
import sys
import time

def test_dns_resolution(hostname):
    """Tester la résolution DNS d'un nom d'hôte"""
    try:
        print(f"Test DNS pour {hostname}...")
        answers = dns.resolver.resolve(hostname, 'A')
        for answer in answers:
            print(f"  ✓ {hostname} -> {answer}")
        return True
    except Exception as e:
        print(f"  ✗ Erreur DNS pour {hostname}: {e}")
        return False

def test_socket_connection(hostname, port):
    """Tester la connexion socket directe"""
    try:
        print(f"Test socket pour {hostname}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        if result == 0:
            print(f"  ✓ Connexion socket réussie")
            return True
        else:
            print(f"  ✗ Connexion socket échouée (code: {result})")
            return False
    except Exception as e:
        print(f"  ✗ Erreur socket pour {hostname}:{port}: {e}")
        return False

def test_http_request(url):
    """Tester une requête HTTP"""
    try:
        print(f"Test HTTP pour {url}...")
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'FinData-IA-MK/1.0'
        })
        print(f"  ✓ HTTP {response.status_code} - {len(response.content)} bytes")
        return True
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout pour {url}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"  ✗ Erreur de connexion pour {url}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Erreur HTTP pour {url}: {e}")
        return False

def test_scrapedo_api():
    """Tester l'API Scrape.do"""
    try:
        print("Test API Scrape.do...")
        # Test avec une URL simple
        test_url = "https://httpbin.org/html"
        response = requests.get("https://api.scrape.do/", params={
            "token": "test_token",
            "url": test_url
        }, timeout=10)
        print(f"  ✓ API Scrape.do accessible (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"  ✗ Erreur API Scrape.do: {e}")
        return False

def main():
    print("=== Diagnostic de connectivité réseau ===\n")
    
    # Test DNS
    hosts_to_test = [
        "api.scrape.do",
        "www.lefigaro.fr",
        "httpbin.org",
        "google.com"
    ]
    
    print("1. Tests de résolution DNS:")
    for host in hosts_to_test:
        test_dns_resolution(host)
    print()
    
    # Test socket
    print("2. Tests de connexion socket:")
    test_socket_connection("api.scrape.do", 443)
    test_socket_connection("www.lefigaro.fr", 443)
    test_socket_connection("httpbin.org", 443)
    print()
    
    # Test HTTP
    print("3. Tests de requêtes HTTP:")
    test_http_request("https://httpbin.org/html")
    test_http_request("https://www.lefigaro.fr/actualite-france/")
    print()
    
    # Test Scrape.do
    print("4. Test API Scrape.do:")
    test_scrapedo_api()
    print()
    
    print("=== Diagnostic terminé ===")

if __name__ == "__main__":
    main() 