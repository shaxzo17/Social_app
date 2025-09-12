import requests
from django.conf import settings

def eskiz_login():
    url = "https://notify.eskiz.uz/api/auth/login"
    data = {
        "email": settings.ESKIZ_EMAIL,
        "password": settings.ESKIZ_PASSWORD
    }
    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json().get("data", {}).get("token")
    else:
        raise Exception(f"Eskiz login xato: {response.text}")


def send_phone(phone_number, code):
    try:
        token = eskiz_login()
        url = "https://notify.eskiz.uz/api/message/sms/send"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        data = {
            "mobile_phone": phone_number,
            "message": f"Sizning tasdiqlash kodingiz: {code}",
            "from": "4546"
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code != 200:
            print("SMS yuborishda xatolik:", response.text)
        else:
            print(f"SMS yuborildi -> {phone_number}, code: {code}")

        return response.json()
    except Exception as e:
        print("SMS yuborishda xatolik:", e)
        return None
