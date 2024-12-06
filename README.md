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

1. client send an authentication request

2. 