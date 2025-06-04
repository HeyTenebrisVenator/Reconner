import os
import codecs
import mmh3
import requests
from colorama import Fore
#DEFINE AS VARIÁVEIS
URL = input(Fore.CYAN + "URL  >>  " + Fore.YELLOW)
try:
    requests.get(URL)
    print(Fore.GREEN + "OK" + Fore.RESET)
except Exception as e:
    print(Fore.RED + "ERROR! " + e + Fore.RESET)
    exit()

Local_save = input(Fore.CYAN + "SAVE LOCAL  >>  " + Fore.YELLOW)
try:
    os.listdir(Local_save)
except Exception as e:
    print(Fore.RED + "ERROR! " + e + Fore.RESET)

Domain = URL.replace("https://", "").replace('http://','').split('/')[0]


Page_model = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><<URL>></title>
    <style>h1{font-size: 90px;text-align: center;}</style>
</head>
<body>
    <h1><<URL>></h1>
    <h3>Screenshot<h3>
    <<screenshot>>
    <br>
    <h2>Services</h2>
    <h4>Httpx Report</h4>
    <p><<httpx report>></p>
    <br>
    <h4>Nmap Report</h4>
    <p><<nmap report>></p>
    <br>
    <h4>Whatweb Report</h4>
    <p><<whatweb report>></p>
    <br>
    <h4>Whois Report</h4>
    <p><<whois report>></p>
    <br>
    <h2>DIRECTORIES</h2>
    <p><<all dirs>></p>
    <br>
    <h2>OTHERS</h2>
    <h4>Favicon</h4>
    <p><<favicon>></p>
    <br>
    <h4>WAF</h4>
    <p><<waf>></p>

    <br><br>

</body>
</html>"""

print(Fore.RESET)

def Create_Dir(Local_save, Domain):
    try:
        os.mkdir(f"{Local_save}/{Domain}")
    except:
        pass
    return f"{Local_save}/{Domain}"

def Screenshot(Domain, Local_save):
    os.system(f'cd {Local_save} ;sudo httpx -u {Domain} -ss ')

def CollectServices(Domain, Local_save, URL):
    os.system(f'sudo httpx -u {Domain} -td -nc | sudo tee {Local_save}/httpx_services') #httpx
    os.system(f'sudo nmap {Domain} -sV -A -O  | sudo tee {Local_save}/nmap_services') # nmap
    os.system(f'sudo whatweb {URL} -a 3 --color never | sudo tee {Local_save}/whatweb_services') # nmap
    os.system(f'sudo whois {Domain} | sudo tee {Local_save}/whois')

def DirCollect(URL, Domain,Local_save):
    os.system(f'sudo katana -cs {Domain} -u {URL} | sudo tee -a {Local_save}/dirs_katana')
    os.system(f'sudo waybackurls {URL} | sudo tee -a {Local_save}/dirs_waybackurls')
    os.system(f'sudo gau {Domain} | sudo tee -a {Local_save}/dirs_gau')
    os.system(f'sudo cat {Local_save}/dirs_waybackurls {Local_save}/dirs_katana {Local_save}/dirs_gau | sort | uniq -u | sudo httpx | sudo tee -a {Local_save}/all_dirs')

def Favicon(URL, Local_Save):
    try:
        response = requests.get(f'{URL}/favicon.ico')
        if response.status_code == 200:
            favicon = codecs.encode(response.content, 'base64')
            hash = mmh3.hash(favicon)
            return hash
    except:
        print('ERRO')
        return "ERRO"

def Waf(Domain, Local_Save):
    os.system(f"sudo wafw00f {Domain} --no-color | grep 'behind' | tee -a {Local_save}/wafw00f")
    return open(f"{Local_save}/wafw00f", 'r').read()

Local_save = Create_Dir(Local_save=Local_save, Domain=Domain)

Screenshot(Domain=Domain, Local_save=Local_save)
Local_screenshot = f"{Local_save}/output/screenshot/{Domain}/{os.listdir(f"{Local_save}/output/screenshot/{Domain}")[0]}"

CollectServices(Domain=Domain,Local_save=Local_save,URL=URL)
Local_httpx = open(f"{Local_save}/httpx_services",'r').read().split('[')[1].replace(']', '')
Local_nmap = open(f"{Local_save}/nmap_services",'r').read().replace('\n', '<br>')
Local_whatweb = open(f"{Local_save}/whatweb_services", 'r').read().replace('\n', '<br><br>')
Local_whois = open(f"{Local_save}/whois",'r').read().replace('\n', '<br>')

DirCollect(URL=URL, Domain=Domain, Local_save=Local_save)
Local_dirs = open(f"{Local_save}/all_dirs", 'r').read().replace("\n", "<br><br>")
os.system(f"sudo chmod 777 -R {Local_save}")
Fav = str(Favicon(URL=URL, Local_Save=Local_save))
if Fav == None:
    Fav = "NO"
WAF = Waf(Domain=Domain, Local_Save=Local_save)


Page_model = Page_model.replace('<<URL>>', Domain).replace('<<screenshot>>', f'<img src={Local_screenshot}>').replace('<<nmap report>>', Local_nmap).replace('<<whatweb report>>', Local_whatweb).replace('<<httpx report>>', Local_httpx).replace('<<whois report>>', Local_whois).replace('<<all dirs>>', Local_dirs).replace("<<favicon>>", Fav).replace("<<waf>>", WAF)

open(f"{Local_save}/report.html", 'w').write(Page_model)