import requests
import json

# Test OTP request
print("Testing OTP request...")
otp_response = requests.post('http://localhost:8000/api/otp/request', json={
    'channel': 'email',
    'email': 'test@example.com'
})
print(f"OTP Request Status: {otp_response.status_code}")
print(f"OTP Response: {otp_response.text}")

if otp_response.status_code == 200:
    data = otp_response.json()
    challenge_id = data.get('challenge_id')
    print(f"Challenge ID: {challenge_id}")

    # Test OTP verification
    print("\nTesting OTP verification...")
    verify_response = requests.post('http://localhost:8000/api/otp/verify', json={
        'challenge_id': challenge_id,
        'otp': '123456'
    })
    print(f"OTP Verify Status: {verify_response.status_code}")
    print(f"OTP Verify Response: {verify_response.text}")

    if verify_response.status_code == 200:
        token = verify_response.json().get('token')
        print(f"Login successful! Token: {token[:20]}...")

        # Test authenticated endpoint
        print("\nTesting authenticated endpoint...")
        me_response = requests.get('http://localhost:8000/api/me', headers={
            'Authorization': f'Bearer {token}'
        })
        print(f"Me Status: {me_response.status_code}")
        print(f"Me Response: {me_response.text}")
else:
    print("OTP request failed!")