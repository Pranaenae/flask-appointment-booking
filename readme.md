Ping app
```
curl http://127.0.0.1:5000/
```

Fetch jwt token

```
curl http://127.0.0.1:5000/login -H "Content-Type: application/json" -d '{"username":"testuser","password":"password123"}' -v
```

Send with auth header.

```
curl -X GET http://127.0.0.1:5000/protected -H "Authorization: Bearer <JWT>"
```

Appointments.
```
curl -X GET http://127.0.0.1:5000/appointments\?date\=2025-01-15 -H "Authorization: Bearer <JWT>" 
```
Start the app
```
flask --app main run --debug
```
