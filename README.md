# connectivity-api

## Installation

Clone this repo

```bash
git clone git@code.siemens.com:xxx.git
```

Build and run!

```bash
docker-compose up --build -d
```

From now on, you will be able to send your requests under http://localhost:7778

## GET endpoints:

`GET /`
API welcome page

`GET /health`
API health check

`GET /listfiles`
Lists sample local files that can be encrypted

`GET /download/{id}`
Downloads encrypted file with given job ID. Returns either the binary or HTTP_404

## POST endpoints:

`POST /api/agentmanagement/v3/encrypt`
Either gets a local file or a URL with a key to encrypt. Returns job ID
~~~~
scenario-1 for request: {"key": "samplepassword", "filename": "file4.iso"}
scenario-2 for request: {"key": "samplepassword", "url": "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg"}
~~~~

`POST /api/agentmanagement/v3/decrypt`
Decrypts (previously encrypted) file by consuming given job ID
~~~~
example request: {"id": "ip1uplfmvfz519jb"}
~~~~

`POST /api/agentmanagement/v3/check`
Returns job status for encryption by consuming given job ID
~~~~
example request: {"id": "ip1uplfmvfz519jb"}
~~~~

## TODOs

`POST /api/agentmanagement/v3/register`
Returns dummy response

`POST /api/agentmanagement/v3/register/{agent_id}`
Returns dummy response

`POST /api/agentmanagement/v3/oauth/token`
Returns dummy response

`POST /api/agentmanagement/v3/exchange`
Returns dummy response


### EOF
