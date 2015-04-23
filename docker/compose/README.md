Docker-compose
==============

The docker-compose container runs the latests docker-compose & Docker within a container.

# Usage:

The Docker socket needs to be mounted as a volume to control Docker on the host. A source folder must be mounted to access the docker-compose definition


## Build & Run

_Move to the `ckan-docker` directory_

- Build it:

_Build the Docker image from `docker/compose/Dockerfile`, and call it "dockercompose_container"_

	docker build --tag="dockercompose_container" docker/compose

- Run it:

_Start the a container based on the `dockercompose_container` Docker image_

	docker run -it -d --name="dockercompose-ckan" -p 2375 -v /var/run/docker.sock:/tmp/docker.sock -v $(pwd):/src dockercompose_container

- Set the source volume path to yours.

_In the docker-compose container docker-compose won't work with relative path, because the mount namespace is different, you need to change the relative path to absolute path_

for example, change the `./`:

	volumes:
	    - ./_src:/usr/lib/ckan/default/src

to an absolute path  to you ckan-docker directory: `/Users/username/git/ckan/ckan-docker/`

	volumes:
	    - /Users/username/git/ckan/ckan-docker/_src:/usr/lib/ckan/default/src

- Build the Docker images & run the containers:

Send the `docker-compose up` command to the docker-compose container

	docker exec -it dockercompose-ckan docker-compose up


## Using the Docker-compose container

You can use any docker-compose command by pre-pending the `docker exec -it dockercompose-ckan` command to any docker-compose command

### build & start / recreate

	docker exec -it dockercompose-ckan docker-compose up

### stop it

	docker exec -it dockercompose-ckan docker-compose stop

### start it

	docker exec -it dockercompose-ckan docker-compose start

### delete the containers

	docker exec -it dockercompose-ckan docker-compose rm

### build new images

	docker exec -it dockercompose-ckan docker-compose build

### logs

	docker exec -it dockercompose-ckan docker-compose logs
