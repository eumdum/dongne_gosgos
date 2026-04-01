import requests
import json
import environ

env = environ.Env()

def verify_business_number(b_no):
    service_key = env('BUSINESS_API_KEY')
    url = f"https://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey={service_key}"
    
    if b_no == "0000000000":  # 테스트용
        return True
        
    payload = json.dumps({"b_no": [b_no]}) 
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, data=payload, headers=headers)
        res_data = response.json()
        
        if res_data.get('data')[0].get('b_stts_cd') == '01':  # 01이면 통과임
            return True
        return False
    except:
        return False