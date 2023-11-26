# Ben's Ebay scraper script
# I don't know how it works but it works

import pandas as pd
import sys
# HTTP request stuff
import json
import requests
import browser_cookie3


# You need to be signed into an Ebay seller account to access Terapeak
# Log into Ebay on a seller account on Google Chrome, then close the browser so this script can yoink your cookies.
try:
    cookies = browser_cookie3.chrome(domain_name='ebay.com')
except PermissionError:
    print("Permission Error - Please close Chrome so I can access your browser cookies, you may reopen it after launching the script.", file=sys.stderr)
    exit(1)

cookie_dict = dict()
for i in cookies:
    cookie_dict[i.name] = i.value


def get_gpu_data(gpu_model: str, price_low: int, price_high: int):
    """Get historical price/sell volume data for a particular GPU

    Args:
        gpu_model (str): GPU model to search for e.g. Geforce GTX 1080, Geforce RTX 3070, etc.
        price_low (int): Minimum price to search for. e.g. remove all listings for GPU's at $0.01
        price_high (int): Maximum price to search for. e.g. remove all listings for GPU's at $999999999

    Returns:
        (list[list], list[list]): List of price data, list of sell volume data
    """
    gpu_model = '+'.join(gpu_model.split(' '))
    url = f'https://www.ebay.com/sh/research/api/search?marketplace=EBAY-US&keywords={gpu_model}&dayRange=CUSTOM&endDate=1699680274511&startDate=1605072274511&categoryId=27386&conditionId=1000&minPrice={price_low}&maxPrice={price_high}&offset=0&limit=50&tabName=SOLD&tz=America%2FLos_Angeles&modules=metricsTrends'
    response = requests.get(url, cookies=cookie_dict)
    rlist = response.text.split('\n')
    requests_json = json.loads(rlist[2])
    # Prices data, Volume sold data
    if 'series' not in requests_json:
        return None, None
    if 'data' not in requests_json['series'][0]:
        return None, None
    return requests_json['series'][0]['data'], requests_json['series'][1]['data']



def get_cpu_data(cpu_model: str, price_low: int, price_high: int):
    """Get historical price/sell volume data for a particular CPU

    Args:
        gpu_model (str): CPU model to search for e.g. Ryzen 3700x
        price_low (int): Minimum price to search for. e.g. remove all listings for CPU's at $0.01
        price_high (int): Maximum price to search for. e.g. remove all listings for CPU's at $999999999

    Returns:
        (list[list], list[list]): List of price data, list of sell volume data
    """
    cpu_model = '+'.join(cpu_model.split(' '))
    url = f'https://www.ebay.com/sh/research/api/search?marketplace=EBAY-US&keywords={cpu_model}&dayRange=CUSTOM&endDate=1699680274511&startDate=1605072274511&categoryId=164&conditionId=1000&minPrice={price_low}&maxPrice={price_high}&offset=0&limit=50&tabName=SOLD&tz=America%2FLos_Angeles&modules=metricsTrends'
    response = requests.get(url, cookies=cookie_dict)
    rlist = response.text.split('\n')
    requests_json = json.loads(rlist[2])
    # Prices data, volume sold data
    if 'series' not in requests_json:
        return None, None
    if 'data' not in requests_json['series'][0]:
        return None, None
    return requests_json['series'][0]['data'], requests_json['series'][1]['data']



nvidia_gpu_list = [('Geforce GTX 960', 80, 300), ('Geforce GTX 970', 80, 300), ('Geforce GTX 980', 130, 320), ('Geforce GTX 1060', 100, 300), ('Geforce GTX 1070', 120, 400), ('Geforce GTX 1080', 150, 700), ('Geforce GTX titan', 200, 1400), ('Geforce RTX 2060', 150, 800), ('Geforce RTX 2070', 150, 900), ('Geforce RTX 2080', 200, 1200), ('Geforce RTX titan', 300, 2200), ('Geforce RTX 3060', 200, 1200), ('Geforce RTX 3070', 250, 1600), ('Geforce RTX 3080', 400, 2300), ('Geforce RTX 3090', 500, 3200), ('Geforce RTX 4060', 300, 500), ('Geforce RTX 4070', 400, 1000), ('Geforce RTX 4080', 600, 1600), ('Geforce RTX 4090', 700, 3000)]

amd_gpus = [('Radeon R9 290', 100, 1500), ('Radeon R9 290X', 100, 1500), ('Radeon RX 470', 100, 1500), ('Radeon RX 480', 100, 1500), ('Radeon RX 570', 100, 1500), ('Radeon RX 580', 100, 1500),
            ('Radeon RX 6700 XT', 100, 1500), ('Radeon RX 6800 XT', 100, 2500), ('Radeon RX 6900 XT', 100, 2500), ('Radeon 5600 XT', 100, 2500), ('Radeon RX 6600 XT', 100, 2500),
            ('Radeon RX 6600', 100, 2500), ('Radeon RX 6700', 100, 2500), ('Radeon RX 7900 XT', 100, 2500), ('Radeon RX 7800 XT', 100, 2500), ('Radeon RX 7700 XT', 100, 2500),
            ('Radeon RX 6950 XT', 100, 2500), ('Radeon RX 6750 XT', 100, 2500), ('Radeon RX 6650 XT', 100, 2500), ('Radeon RX 6500 XT', 100, 2500), ('Radeon RX 5500 XT', 100, 2500),
            ('Radeon RX 5700 XT', 100, 2500)]

gpu_price_df = pd.DataFrame(columns=['timestamp', 'price', 'null', 'model'])
gpu_volum_df = pd.DataFrame(columns=['timestamp', 'volume', 'null', 'model'])

gpu_list = nvidia_gpu_list + amd_gpus

for gpu in gpu_list:
    print(gpu)
    prices, vol = get_gpu_data(*gpu)
    if prices == None:
        continue
    tmp_df = pd.DataFrame(prices, columns=['timestamp', 'price', 'null'])
    tmp_df['model'] = len(tmp_df) * [gpu[0]]
    gpu_price_df = gpu_price_df.merge(tmp_df, how='outer')

    tmp_df2 = pd.DataFrame(vol, columns=['timestamp', 'volume', 'null'])
    tmp_df2['model'] = len(tmp_df2) * [gpu[0]]
    gpu_volum_df = gpu_volum_df.merge(tmp_df2, how='outer')

gpu_price_df.to_csv('./gpu_prices.csv', index=False)
gpu_volum_df.to_csv('./gpu_volume.csv', index=False)



amd_cpus = [('Ryzen 7 1700X', 100, 500), ('Ryzen 7 1700', 100, 500),
            ('Ryzen 7 1800X', 100, 800), ('Ryzen 5 1400', 100, 800), ('Ryzen 5 1500X', 100, 800), ('Ryzen 5 1600X', 100, 800), ('Ryzen 5 1600', 100, 800), ('Ryzen 3 1200', 100, 800),
            ('Ryzen 3 1300x', 100, 800), ('Ryzen 3 1300x', 100, 800), ('Ryzen Threadripper 2950X', 100, 1300), ('Ryzen 5 2600X', 100, 800), ('Ryzen 5 2600', 100, 800),
            ('Ryzen 7 2700X', 100, 800), ('Ryzen 7 2700', 100, 800), ('Ryzen 5 3600X', 100, 800), ('Ryzen 5 3600', 100, 1000), ('Ryzen 7 3700X', 100, 1000), ('Ryzen 7 3800X', 100, 1000),
            ('Ryzen 9 3900X', 100, 1000), ('Ryzen 9 3950X', 100, 2500), ('Ryzen Threadripper 3990X', 100, 2500), ('Ryzen 5 5600X', 100, 1500), ('Ryzen 7 5800X', 100, 1500),
            ('Ryzen 9 5900X', 100, 1500), ('Ryzen 9 5950X', 100, 1500), ('Ryzen 7 5800X', 100, 1500), ('Ryzen 7 5800', 100, 1500), ('Ryzen 9 5900', 100, 1500),
            ('Ryzen 7 5800X3D', 100, 1500), ('Ryzen 3 4100', 100, 1500), ('Ryzen 5 5500', 100, 1500), ('Ryzen 5 4500', 100, 1500), ('Ryzen 5 5600', 100, 1500), ('Ryzen 7 5700', 100, 1500),
            ('Ryzen 5 7600X', 100, 1500), ('Ryzen 7 7700X', 100, 1500), ('Ryzen 9 7900X', 100, 1500), ('Ryzen 9 7950X', 100, 1500), ('Ryzen 5 7600', 100, 1500), ('Ryzen 7 7700', 100, 1500),
            ('Ryzen 9 7900', 100, 1500), ('Ryzen 9 7900X3D', 100, 1500), ('Ryzen 9 7950X3D', 100, 1500), ('Ryzen 7 7800X3D', 100, 1500), ('Ryzen 5 5600X3D', 100, 1500)]
intel_cpu = [('Core i5-4430S',1,1800),('Core i5-4570R',10,1800),('Core i5-4570S',1,16275),('Core i5-4570T',3,3850,),('Core i5-4670K',5,1520),('Core i5-4670R',140,140),('Core i7-4770K',4,1120),
             ('Core i7-4820K',2,960),('Core i7-4930K',5,500),('Core i7-4960X',35,975),('Core i5-4690K',1,1520),('Core i7-4790K',3,1610),('Core i7-5820K',4,375),('Core i7-5930K',7,360),
             ('Core i7-5960X',5,545),('Core i5-5675C',12,130),('Core i7-5775C',16,192),('Core i5-6600K',8,1300),('Core i7-6700K',9,2400),('Core i7-6800K',1,532),('Core i7-6850K',5,440),(
                 'Core i7-6900K',50,650),('Core i7-6950X',5,1350),('Core i3-7350K',12,170),('Core i5-7600K',1,1013),('Core i7-7700K',3,3300),('Core i5-7640X',30,280),('Core i7-7740X',30,790),
             ('Core i7-7800X',17,560),('Core i7-7820X',13,2750),('Core i9-7900X',11,750),('Core i9-7920X',1,560),('Core i9-7940X',32,560),('Core i9-7960X',41,900),('Core i9-7980XE',20,990),
             ('Core i3-8350K',7,240),('Core i5-8600K',20,420),('Core i7-8700K',6,10500),('Core i7-8086K',60,650),('Core i7-9800X',78,500),('Core i9-9820X',35,500),('Core i9-9900X',46,995),
             ('Core i9-9920X',90,950),('Core i9-9940X',63,800),('Core i9-9960X',133,830),('Core i9-9980XE',50,1400),('Core i5-9600K',14,350),('Core i7-9700K',4,8151),('Core i9-9900K',5,3551),
             ('Core i3-9350KF',55,230),('Core i5-9600KF',30,350),('Core i7-9700KF',14,1247),('Core i9-9900KF',12,3050),('Core i3-9350K',115,115),('Core i9-9900KS',5,3551),('Core i9-10900X',43,750),
             ('Core i9-10920X',8.960, 2000),('Core i9-10940X',50,1200),('Core i9-10980XE',10,1800),('Core i5-10600K',10,420),('Core i7-10700K',6,887),('Core i9-10900K',5,2000),('Core i9-10850K',19,1130),
             ('Core i5-11600K',10,450),('Core i7-11700K',5,4500),('Core i9-11900K',12,1200),('Core i5-12600K',30,510),('Core i7-12700K',7,4175),('Core i9-12900K',1,2000),('Core i3-12100F',34,189),('Core i5-13600K',1,600),
             ('Core i7-13700K',11,750),('Core i9-13900K',1,1630),('Core i3-13100F',45,280),('Core i3-13100T',100,119),('Core i5-13400T',140,215),('Core i5-13400F',130,241),('Core i7-13700F',225,427),('Core i7-13700T',100,400),
             ('Core i9-13900F',395,675),('Core i9-13900T',305,655),('Core i9-13900KS',1,1630)]



cpu_price_df = pd.DataFrame(columns=['timestamp', 'price', 'null', 'model'])
cpu_volum_df = pd.DataFrame(columns=['timestamp', 'volume', 'null', 'model'])

cpu_list = amd_cpus + intel_cpu

for cpu in cpu_list:
    print(cpu)
    prices, vol = get_cpu_data(*cpu)
    if prices == None:
        print(f'{cpu} skipped')
        continue
    tmp_df = pd.DataFrame(prices, columns=['timestamp', 'price', 'null'])
    tmp_df['model'] = len(tmp_df) * [cpu[0]]
    cpu_price_df = cpu_price_df.merge(tmp_df, how='outer')

    tmp_df2 = pd.DataFrame(vol, columns=['timestamp', 'volume', 'null'])
    tmp_df2['model'] = len(tmp_df2) * [cpu[0]]
    cpu_volum_df = cpu_volum_df.merge(tmp_df2, how='outer')

cpu_price_df.to_csv('./cpu_prices.csv', index=False)
cpu_volum_df.to_csv('./cpu_volume.csv', index=False)


get_cpu_data(*('Ryzen 3990X', 100, 2500))


