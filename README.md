## iOS Token and Password based Multi-factor authentication system 

Multi-factor authentication system using iOS app token and password.

### Structure

Server

- running python.

- listens to a http request

- stores list of trust usernames

Client

- running on iOS

- send a request to server. including  username and password

- check the location

- get a token

### Pipeline

1. client send an authentication request, with a username

2. server check if the location in the legal range

3. if valid location, send a one time code, start a timer, one time code expires 1 min

4. user get the one time code and input username, OTP, real password to the server

5. user get access

### Communication Protocol

1. For OTP:


```
client -> server
username,location
xxxxxxx,xxx.xxxx:xxx.xxxx

server -> client
{otp:xxxxxx}

```

2. For 