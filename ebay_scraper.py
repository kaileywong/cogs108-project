import pandas as pd

# HTTP request stuff
import json
import requests
import browser_cookie3

try:
    cookies = browser_cookie3.chrome(domain_name='ebay.com')
except PermissionError:
    print("Permission Error - Please close Chrome so I can access your browser cookies, you may reopen it after launching the script.", file=sys.stderr)
    exit(1)

cookie_dict = dict()
for i in cookies:
    cookie_dict[i.name] = i.value