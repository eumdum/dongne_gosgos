import requests
import json
import environ

env = environ.Env()

def verify_business_number(b_no):
    service_key = env('BUSINESS_API_KEY')
    url = f"https://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey={service_key}"
    
    if b_no == "0000000000": return True,  # 테스트용  

    payload = json.dumps({"b_no": [b_no]}) 
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, data=payload, headers=headers)
        res_data = response.json()

        biz_info = res_data.get('data')[0]
        status_code = biz_info.get('b_stts_cd') # 01:계속, 02:휴업, 03:폐업
        status_msg = biz_info.get('b_stts')

        if status_code == '01':
            return True, status_msg
        else:
            return False, status_msg
        
        # if res_data.get('data')[0].get('b_stts_cd') == '01':  # 01이면 통과임
        #     return True
        # return False
    except:
        return False, "조회 오류"