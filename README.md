## Problem 
We want to implement an authentication service for API-REST calls closely following the OAUTH2 "authorization code" grant type protocol. The service will have 3 distinct components (which should be implemented as 3 independent docker containers): The client-side webapp, the oauth2 authorization server and the resource server (see the image below as an example).
In our use case we will follow a simple no-UI approach. Our end users will make `curl` calls to the client-side webapp, which will obtain the answers by calling an API in the resource server. The process will be done following an oauth2 “authorization code” grant type protocol.

In this exercise we would like to implement only 2 calls: `/current_time`, to retrieve the current server time (any standard format you want), and `/epoch_time` to retrieve the current time as number of seconds since epoch. The web api can send these back to the user via json output

A good resource to learn/refresh what oauth2 does is [here](https://oauth.net/2/grant-types/authorization-code/)
An illustration example of how the OAUTH2 protocol works is shown in the image below, taken from [here](https://docs.oracle.com/cd/E82085_01/160023/JOS%20Implementation%20Guide/Output/oauth.htm):
![Oauth2 example](https://docs.oracle.com/cd/E82085_01/160023/JOS%20Implementation%20Guide/Output/img/oauth2-arch.png)

Here are some important points to take into account:

* In oauth2 the application first registers itself with the oauth authentication server. We will consider that such registration has already been performed where the application properly registered a callback url to it and the app received a client ID = "1234" and client secret = "qwerty".
* On the authentication step we will skip the request to the user to authenticate himself via a UI. In this exercise we will consider that access is ALWAYS granted to the user without the need to prompt him for password or any other credentials. The authorization server will therefore send back to the web app the authorization grant right away for the two endpoints proposed above. Note that the user should only be allowed to call the 2 endpoints defined above, any other use should not be granted an authorization.
* The session token obtained by the webapp server should be short-lived (5 seconds) and should only give access to the particular endpoint the user has requested. For this exercise we will consider that each individual user call triggers the request of a new token. Session tokens should be encoded using [JWT format](https://jwt.io). 
* Finally, the webapp server should be able to access the resource server by submitting an API call to it and providing the session token obtained. The resource server should validate the session token and check that the requested endpoint and user are correct before serving back the information. 
* Implementation of this exercise should be done in python and using 3 different docker containers joined together using docker_compose. It should be possible to run the exercise by just executing the docker compose, providing an entrypoint to the webapp server to perform the `curl` calls.

## Oauth2 flow details
Oauth2 protocol has 3 distinct components:
1. webapp 
2. resource server
3. oauth2 server


The protocol supports several flows of acquiring the access token from the oauth2 server and they depend on the type of the application (third party, first party, client side or server side). In the current implementation we assume that the application (webapp) is a first party application (developed by the same company as the resource server), i.e. it can ask user for his credentials (username and password) and provide them to the oauth2 server. But for simplicity sake we just send any username/password pair and the oauth2 server must accept them, to skip the interaction with the user.
So the flow looks like that: 
1. User calls webapp by `curl`.
2. Webapp requests access token from the oauth2 server.
3. Oauth2 server validates the application and if everything is OK. Issues a new access token in the JWT format.
3. Webapp gets access token from the oauth2 server. The token is short-lived so we don’t store it in webapp and request it on every user call. Webapp calls the API (resource server) providing the access token to get the information that user wants.
4. Resource server asks oauth2 server to validate and get the information about the access token. 
5. Oauth2 server decodes JWT access token and validates the payload and the expiration time. If everything is fine it returns
all information contained in the JWT payload.
6. Resource server receives token information. It checks that requested resource within the token scope if so resource server returns the data. In this case it’s just current time or timestamp.
5. Webapp shows result obtained from the resource server to the user.


## Design and implementation details 
* All services (webapp, oauth2 server, resource server) are implemented in python3.7 and Flask. They are wrapped in separate docker containers and can be easily started by `docker-compose up`. There is no persistence layer since we only need to store registered oauth2 applications and for the simplicity they are stored in the memory.
* Services are built in the spirit of the [go-kit](https://github.com/go-kit/kit) library. So the transport layer (http and Flask) is only responsible for obtaining data from the http request and returning data as http json response. The business logic layer lives separately and knows nothing about http protocol or Flask. It allows us to easily switch from http and json to gRPC and protobuf without touching the core logic. And we don’t bound to a specific web framework.
* All services are well covered with unit tests using `pytest` library. They test only code and don’t depend on other services and the environment they are running in.
* All logs are structured and follow an event message style. Logs are formatted as json to simplify further parsing and investigation in production.
* Services have the default configuration to work without providing any settings. In the meantime they can be configured for the specific environment (`production`, `stage`, `development` or `testing`) via `configs/application_config.py` file. This file must be provided by the environment and it won’t get into VCS and docker image.
* All external data is validated via json schema to be sure that we fail as soon as possible in cause of invalid data.


# Run locally
You will need `docker` and `docker-compose` installed. 
In the project root type: `docker-compose up`
This will build 3 docker images for each service and start 3 containers. After that you can call the webapp service:

`curl http://localhost:5003/current_time`

`curl http://localhost:5003/epoch_time`


# Run tests
You will need `docker` and `docker-compose` installed. 
In the project root type: `docker-compose build` to build a docker image for each service, if you didn’t build them before.
After that in the project root run:
` ./run-unittests-docker.sh`


## Some further improvements:
The code base is ready for production in general. But of course there are something that should be done to ensure good maintaining and scaling in the future.
* Add Sentry support to see all errors in production.
* Use python context variables to store request bound values such as user_id, client_id, request_id and blend them into each log record via logging.Filter. It will simplify logs investigation.
* Add code style check to the project. Since there are python annotations in the project we may add static linter too.
* Split python requirements into main and dev specific or probile use more advanced requirements management tool.
* Right now unit tests are testing services at the higher level: they call views and receive https responses. They test all modules that are involved in the request processing. It goes against the rule of unit tests actually :) So a better approach is to test every layer separately and mock layers beneath. I.e. we could test API clients layer, service layer; http layer. But since the logic is pretty simple and the request flow is flat it’s OK to test all cases at the higher (views, http) level.
