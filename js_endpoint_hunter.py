import requests
import re
import sys
from colorama import Fore, init
from urllib.parse import urljoin, urlparse

init(autoreset=True)

BANNER = """
     ██╗███████╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
     ██║██╔════╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
     ██║███████╗    ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██   ██║╚════██║    ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
╚█████╔╝███████║    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
 ╚════╝ ╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
          JS Endpoint Hunter - By Ambuj Tiwari
          Bug Bounty | VAPT | Recon Tool
"""

def get_js_files(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', r.text)
        full_urls = []
        for js in js_files:
            if js.startswith("http"):
                full_urls.append(js)
            else:
                full_urls.append(urljoin(url, js))
        return full_urls
    except Exception as e:
        print(Fore.RED + f"[!] Error fetching page: {e}")
        return []

def extract_endpoints(js_url):
    endpoints = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(js_url, headers=headers, timeout=10, verify=False)
        
        # Extract API endpoints and paths
        patterns = [
            r'["\'](/api/[^\s"\'<>]*)["\']',
            r'["\'](/v[0-9]/[^\s"\'<>]*)["\']',
            r'["\']([^\s"\'<>]*\.(php|asp|aspx|jsp|json|xml))["\']',
            r'fetch\(["\']([^\s"\'<>]*)["\']',
            r'axios\.[a-z]+\(["\']([^\s"\'<>]*)["\']',
            r'url:\s*["\']([^\s"\'<>]*)["\']',
            r'(https?://[^\s"\'<>]+)',
        ]
        
        for pattern in patterns:
            found = re.findall(pattern, r.text)
            if found:
                if isinstance(found[0], tuple):
                    endpoints.extend([f[0] for f in found])
                else:
                    endpoints.extend(found)
                    
    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}")
    
    return list(set(endpoints))

def main(url):
    print(Fore.CYAN + BANNER)
    print(Fore.YELLOW + f"[*] Target: {url}")
    print(Fore.YELLOW + "[*] Finding JS files...\n")
    
    js_files = get_js_files(url)
    
    if not js_files:
        print(Fore.RED + "[-] No JS files found!")
        return
    
    print(Fore.GREEN + f"[+] Found {len(js_files)} JS files:\n")
    for js in js_files:
        print(Fore.WHITE + f"  → {js}")
    
    print(Fore.YELLOW + "\n[*] Extracting endpoints from JS files...\n")
    
    all_endpoints = []
    for js in js_files:
        print(Fore.CYAN + f"[*] Scanning: {js}")
        endpoints = extract_endpoints(js)
        all_endpoints.extend(endpoints)
    
    all_endpoints = list(set(all_endpoints))
    
    if all_endpoints:
        print(Fore.GREEN + f"\n[+] Found {len(all_endpoints)} unique endpoints:\n")
        for ep in all_endpoints:
            print(Fore.WHITE + f"  → {ep}")
        
        domain = urlparse(url).netloc
        filename = f"{domain}_endpoints.txt"
        with open(filename, "w") as f:
            f.write("\n".join(all_endpoints))
        print(Fore.GREEN + f"\n[+] Results saved to: {filename}")
    else:
        print(Fore.RED + "[-] No endpoints found.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input(Fore.CYAN + "\nEnter Target URL: ")
    main(target)
