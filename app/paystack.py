import requests
from .config import settings

class PayStack:
    PAYSTASK_SECRET_KEY = settings.paystack_secret_key
    base_url = "https://api.paystack.co"

    def verify_payment(self, ref, *args, **kwargs):
        path = f"/transaction/verify/{ref}"

        headers = {
            "Authorization": f"Bearer {self.PAYSTASK_SECRET_KEY}",
            "Content-type": 'application/json',
        }
        url = self.base_url + path
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'], response_data['data']

        response_data = response.json()
        return response_data['status'], response_data['message'] 