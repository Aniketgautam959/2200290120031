from rest_framework.views import APIView
from rest_framework.response import Response
import requests

from collections import deque

import time

# window size
MAX_NUMBERS = 10

# test servers urls
NUMBER_SOURCES = {
    'p': 'http://20.244.56.144/evaluation-service/primes',
    'f': 'http://20.244.56.144/evaluation-service/fibo',
    'e': 'http://20.244.56.144/evaluation-service/even',
    'r': 'http://20.244.56.144/evaluation-service/rand'
}


recent_numbers = deque(maxlen=MAX_NUMBERS)

class GetNumbers(APIView):
    def get(self, request, num_type):
        if num_type not in NUMBER_SOURCES:
            return Response({"error": "Not a valid number type"}, status=400)

        old_numbers = list(recent_numbers)
        new_numbers_from_api = []

        login_info = {
            "email": "aditya.2226cs1066@kiet.edu",
            "name": "Aditya Madwal",
            "rollNo": "2200290120011",
            "accessCode": "SxVeja",
            "clientID": "ba775e93-70f9-4707-be8b-aa2efdf0594c",
            "clientSecret": "sAvbvPGEnZbspAQB"
        }

        # Get access token : since the token provided by your test servers auth api expires quickly, i have automated the token fecthing process.

        api_token = ""
        try:
            token_response = requests.post('http://20.244.56.144/evaluation-service/auth', json=login_info)
            if token_response.status_code == 201:
                api_token = token_response.json().get('access_token')
            else:
                return Response({"error": "Couldn't login to API"}, status=401)
        except:
            return Response({"error": "Login request failed"}, status=500)

        try:
            start_time = time.time()
            auth_header = {'Authorization': f'Bearer {api_token}'}
            api_response = requests.get(NUMBER_SOURCES[num_type], headers=auth_header, timeout=0.5)
            time_taken = time.time() - start_time

            if api_response.status_code == 200:
                numbers_from_api = api_response.json().get("numbers", [])
                new_numbers_from_api = numbers_from_api

                for n in numbers_from_api:
                    if n not in recent_numbers:
                        recent_numbers.append(n)
                        if len(recent_numbers) > MAX_NUMBERS:
                            recent_numbers.popleft()

        except:
            return Response({"error": "API request failed"}, status=500)

        current_numbers = list(recent_numbers)
        average = round(sum(current_numbers) / len(current_numbers), 2) if current_numbers else 0.00

        return Response({
            "windowPrevState": old_numbers,
            "windowCurrState": current_numbers,
            "numbers": new_numbers_from_api,
            "avg": average
        })