# ELSA Challenge for backend/integrations developer
This is Elsa’s Coding Exercise. It allows Elsa to assess candidates’ ability to develop well structured, maintainable and useful code. The code does not need to be fancy, but needs to represent the coding skills of the candidate, and it will be the basis for discussions on the technical interview. 

You can start this any time you like. It should not take you more than 1 day to code. You can turn it in at any time. As you think about this exercise, please feel to ask questions!

Please Fork this repo and submit your solution in the fork

Happy coding!

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


# Some further improvements:
# Add code style check to the project
# Since there are python annotations in the project we may add static linter
# Add Sentry
# Use python context variables to store request bound values such as user_id, client_id, request_id and blend them into each log record via logging.Filter
# Split python requirements into main and dev specific.
