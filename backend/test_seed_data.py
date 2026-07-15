import requests, json

r = requests.post('http://localhost:8000/api/v1/auth/login', json={'email':'test@qiuzhimiao.com','password':'test123456'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print('=== 简历列表 ===')
r = requests.get('http://localhost:8000/api/v1/resumes', headers=headers)
print('Response:', json.dumps(r.json(), ensure_ascii=False, indent=2))

print('\n=== 岗位列表 ===')
r = requests.get('http://localhost:8000/api/v1/jobs', headers=headers)
print('Response:', json.dumps(r.json(), ensure_ascii=False, indent=2))

print('\n=== 面试记录 ===')
r = requests.get('http://localhost:8000/api/v1/interviews', headers=headers)
print('Response:', json.dumps(r.json(), ensure_ascii=False, indent=2))

print('\n=== 投递记录 ===')
r = requests.get('http://localhost:8000/api/v1/applications', headers=headers)
print('Response:', json.dumps(r.json(), ensure_ascii=False, indent=2))
