# OAuth2 system implementation 
This repository contains implementation of a system that uses OAuth2 protocol. The system consists of 3 distinct components:
* The OAuth2 authorization server.
* The Resource server, i.e. API protected by the OAuth2
* The Webapp, that uses the API. Webapp is server-side (not a single page js application) and in our use case we will follow a simple no-UI approach. Our end users will make `curl` calls to the Webapp, which will obtain the answers by calling an API in the Resource server.

### Some important points about the system:
* Resource server has only 2 endpoints: `/current_time`, to retrieve the current server time (any standard format), and `/epoch_time` to retrieve the current time as number of seconds since epoch.
* In OAuth2 the application first registers itself with the authorization server. We will consider that such registration has already been performed where the application properly registered a callback url to it and the app received a client ID = "1234" and client secret = "qwerty".
* OAuth2 protocol supports several flows of acquiring the access token from the authorization server and they depend on the type of the application (third party, first party, client side or server side). In the current implementation we assume that the application (Webapp) is a first party application (developed by the same company as the resource server), i.e. it can ask user for his credentials (username and password) and provide them to the authorization server. That flow is called `owner password` grant type. For simplicity sake we skip the request to the user to enter his username/password via UI. We consider that OAuth2 server always grants access for any username/password for two endponts proposed above (`/current_time`, `/epoch_time`).
* The access token obtained by the Webapp are short-lived (5 seconds). For simplicity we will consider that each individual user call triggers the request of a new token. Tokens is encoded using [JWT format](https://jwt.io).
* OAuth2 server doesn't support `refresh tokens`. 

### User request flow steps: 
1. User calls webapp via `curl`.
2. Webapp requests an access token from the OAuth2 server.
3. OAuth2 server validates the application and if everything is OK. Issues a new access token in the JWT format.
3. Webapp gets access token from the OAuth2 server. The token is short-lived so we don’t store it in Webapp and request it on every user call. Webapp calls the API (Resource server) providing the access token to get the information that was requested by user.
4. Resource server asks OAuth2 server to validate and get the information about the access token. 
5. OAuth2 server decodes JWT access token and validates the payload and the expiration time. If everything is fine it returns
all information contained in the JWT payload.
6. Resource server receives token information. It checks that requested resource within the token scope if so resource server returns the data. In this case it’s just current time or timestamp.
5. Webapp shows result obtained from the resource server to the user.


# Design and implementation details 
* All services (Webapp, OAuth2 server, Resource server) are implemented in python3.7 and Flask. They are wrapped in separate docker containers and can be easily started by `docker-compose up`. There is no persistence layer since we only need to store registered OAuth2 applications and for the simplicity they are stored in the memory.
* Services are built in the spirit of [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html). So the transport layer (http and Flask) is only responsible for obtaining data from the http request and returning data as http json response. The business logic layer lives separately and knows nothing about the http protocol or Flask. It allows us to easily switch from http and json to gRPC and protobuf without touching the core logic. And we aren't bound to a specific web framework.
* All services are well covered with unit tests using `pytest` library. They test only code and don’t depend on other services and the environment they are running in.
* All logs are structured and follow an event message style. Logs are formatted as json to simplify further parsing and investigation in production.
* Services have the default configuration to work without providing any settings. In the meantime they can be configured for a specific environment (`production`, `stage`, `development` or `testing`) via `configs/application_config.py` file. This file must be provided by the environment and it won’t get into VCS or docker image.
* All external data is validated via json schema to be sure that we fail as soon as possible in case of invalid data.


# Run locally
You will need `docker` and `docker-compose` installed.

In the project root type: `docker-compose up`

This will build 3 docker images for each service and start 3 containers. After that you can call the Webapp service:

`curl http://localhost:5003/current_time`

`curl http://localhost:5003/epoch_time`


# Run tests
You will need `docker` and `docker-compose` installed. 

In the project root type: `docker-compose build` to build a docker image for each service, if you didn’t build them before.

After that in the project root run:

` ./run-unittests-docker.sh`


# Possible further improvements:
The code base is ready for production in general. But of course there are something that should be done to ensure good maintaining and scaling in the future.
* Add Sentry support to see all errors in production.
* Use python context variables to store request bound values such as user_id, client_id, request_id and blend them into each log record via logging.Filter. It will simplify logs investigation.
* Add code style check to the project. Since there are python annotations in the project we may add static linter too.
* Split python application dependencies into main and dev specific or probably use more advanced dependencies management tool, like [poetry](https://python-poetry.org/).
* Right now unit tests are testing services at the higher level: they call views and receive https responses. They test all modules that are involved in the request processing. It goes against the rule of unit tests actually :) So a better approach is to test every layer separately and mock layers beneath. I.e. we could test API clients layer, service layer; http layer. But since the logic is pretty simple and the request flow is flat it’s OK to test all cases at the higher (views, http) level.
