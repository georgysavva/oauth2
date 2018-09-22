# ELSA Challenge for backend/integrations developer

This is Elsa’s Coding Exercise. It allows Elsa to assess candidates’ ability to develop well structured, maintainable and useful code. The code does not need to be fancy, but needs to represent the coding skills of the candidate, and it will be the basis for discussions on the technical interview. 

You can start this any time you like. It should not take you more than 1 day to code. You can turn it in at any time. As you think about this exercise, please feel to ask questions!

Please Fork this repo and submit your solution in the fork

Happy coding!

## Problem 
We want to implement an authentication service for API-REST calls inspired in the OAUTH2 "authorization code" grant type protocol. The service will have 3 distinct components (implemented as 3 independent docker containers): The client-side webapp, the oauth2 authorization server and the resource server.
In our use case, our users will make `curl` calls to the client-side webapp, which will obtain the answers by calling the same endpoint in the resource server after it has obtained proper authentication from the oauth2 server.

In this exercise we would like to implement only 2 calls: `/current_time`, to retrieve the current server time, and `/epoch_time` to retrieve the current time as number of seconds since epoch. 

A good resource to learn/refresh what oauth2 does is [here](https://oauth.net/2/grant-types/authorization-code/)

To build this service, the first thing a developer needs to do in oauth2 is to register their web application with the oauth2 authentication server. We will consider that such registration has already been performed where the application properly registered a callback url to it and the app received a client ID = "1234" and client secret = "qwerty".

Then, when the user makes a call to any of the endpoints in the web application server, we will do:

* First, the webapp server will send an authorization request to the oauth2 authorization server using the client ID and indicating which resource name (endpoint name) it wants to use. In real life this should prompt a request to the user for login and authorization to access these resources from the resources server. In this exercise we will consider that access is ALWAYS granted to the user without the need to prompt him for password or any other credentials. The authorization server will therefore send back tot he web app the authorization grant right away for that endpoint.

* Second, the webapp server will need to request a session token to use the API endpoint. for this it will provide the client ID, the client secret and the authentication token received on the previous step. The received session token is by definition short-lived and should only give access to the particular endpoint the user has requested. For this exercise we will consider that each individual user call triggers the request of a new token. Session tokens should be encoded using [JWT format](jwt.io). 

* Finally, the webapp server should be able to access the resource server by submitting an API call and providing the session token obtained. The resource server will decode the session token and will check that the requested endpoint and user are correct before serving back the information. The webapp will send to the user the information as a json object.


Implementation of this exercise should be done in python and using 3 different docker containers joined together using docker_compose. It should be possible to run the exercise by just executing the docker compose, providing an entrypoing to the webapp server.







An illustration example of how the OAUTH2 protocol works is shown in the image below, taken from [here](https://docs.oracle.com/cd/E82085_01/160023/JOS%20Implementation%20Guide/Output/oauth.htm):
![Oauth2 example](https://docs.oracle.com/cd/E82085_01/160023/JOS%20Implementation%20Guide/Output/img/oauth2-arch.png)

In simple terms, the client (us) uses some client app (in this case we will use a simple curl command) to first call the oauth service to request for a token to use to access some resource. Note that the resource should have previously registered his service with the oauth server so that the oauth server knows it is controlling access to that resource.

The oauth server 

{state problem: needs to be something that involves python coding in classes, integrating some API (hopefully payment or something similar, that has several steps. One of those that have a callback would be nice).}
