## Description  

### What:  

Web-service to markdown appartments' plannings.  

### Done:  
Basic backend (Flask). Mock data, not real images.

### How to start:  

#### Start locally  

1. Start service: `python run.py`  
2. Open main page: `localhost:8000`  
3. use web-service(opened `^^^`) or API calls (`vvv`)

#### Start in docker  

1. Build docker container: `docker-compose up`  
2. Open main page: `localhost:8000`  
3. use web-service(opened `^^^`) or API calls (`vvv`)  

## Web-pages structure:

#### root

[http://localhost:8000](http://localhost:8000)  
redirects to the first unmarked image

#### image page
[http://localhost:8000/123](http://localhost:8000/123)  
shows the template with picture by id


## Backend API:  

#### ID for next not marked image 
**Request:**   
[GET] [http://localhost:8000/next](http://localhost:8000/next)  
**Answer:**  

	{next_unmarked_picture: 0}


#### ID for next not marked image, but not less that %param%
**Request:**  
[GET] [http://localhost:8000/next/123](http://localhost:8000/next/123)  
**Answer:**  

	{next_unmarked_picture: 124}

#### Get image by ID

**Request:**  
[GET] [http://localhost:8000/image/123](http://localhost:8000/image/123)  
**Answer:**  

	<image>

Returns image, `mimetype=image/jpeg`  

#### Get previously saved markdown for image

**Request:**  
[GET] [http://localhost:8000/image/123/markdown](http://localhost:8000/image/123/markdown)  
**Answer:**  

	{
	<json here>
	}

Returns previously saved `json` or `{}` if nothing was saved.

#### Save markdown for image

**Request:**  
[POST] [http://localhost:8000/image/123/markdown](http://localhost:8000/image/123/markdown)  
Payload: any json

	POST /image/1/markdown HTTP/1.1
	HOST: 127.0.0.1:8000
	content-type: application/json
	content-length: 19
	
	{"text":"blabla_1"}
	

**Answer:**  

	{
	msg: "ok"
	}

Saves json for image

#### Root page:

