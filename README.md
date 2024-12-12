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


```
client -> server
username,location
xxxxxxx,xxx.xxxx:xxx.xxxx

server -> client
xxxxxx

```

### Database

```
0|id|INTEGER|0||1
1|username|TEXT|1||0
2|password_hash|TEXT|1||0
3|public_key|TEXT|1||0
4|device_id|TEXT|0||0

0|username|TEXT|1||0
1|login_fail_time|INTEGER|0||0
```

### Usage

For all-python testing:

run server:

```bash
python src/authServer/server.py
```

You will see server listening on port 12345

Then you have 2 choice for running the client

1. Xcode project:

uncomment the following code:

```swift
#preview{
    ContentView()
}
```

for a while you will see the previewed simulator on the screen

click the `send request` button

2. python client:

This python project has the same fucntion as the swift project, except the `CoreLocation` part which is for location authentication, and is for testing and reproducing use when the Xcode project is unavailable because of environment problems.

```bash
python src/authClient/client_test.py
```

The defaut login user is `admin`, and the password is `admin`

If more users are needed, please login as admin and register manually.
