## Setup

Execute

```sh
docker-compose build
```

Then...

```sh
docker-compose run web python3 manage.py migrate
```

Then...

```sh
docker-compose up
```

Run
```sh
docker-compose run web python3 manage.py ingest
```
after adding the CSV file to the appropriate directory.

Part 2:

After the service is running if you hit

```sh
http://0.0.0.0:8000/work/enrich/
```

from some agent (postman, other service) with a body of
```sh
{
  "iswc" : [ISWC1, ISWC2, etc] 
}
```

it will enrich the list with contributors.


If you want to use django Admin page :

run 

```sh
 docker-compose run web python3 manage.py createsuperuser 
 ```
Fill the data accordingly.

Bypass checks if you want.

Use that user (username, pass) to login to admin page.