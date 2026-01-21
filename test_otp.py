import subprocess

result = subprocess.run(['curl', '-s', '-w', '%{http_code}', 'http://localhost:8000/api/otp/request', '-X', 'POST', '-H', 'Content-Type: application/json', '-d', '{"channel":"email","email":"test@example.com"}'], capture_output=True, text=True)
print('OTP Request Status:', result.stdout.strip())