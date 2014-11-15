Fig
===

The Fig container runs Fig version 1.0 & the latest Docker within a container.

# Usage:

The Docker socket needs to be mounted as a volume to control Docker on the host. A source folder must be mounted to access the fig definition


## Build & Run

_Move to the `ckan-docker` directory_

- Build it:

_Build the Docker image from `docker/fig/Dockerfile`, and call it "fig_container"_

	docker build --tag="fig_container" docker/fig

- Run it:

_Start the a container based on the `fig_container` Docker image_

	docker run -it -d --name="fig-ckan" -p 2375 -v /var/run/docker.sock:/tmp/docker.sock -v $(pwd):/src fig_container

- Set the source volume path to yours.

_In the fig container fig won't work with relative path, because the mount namespace is different, you need to change the relative path to absolute path_

for example, change the `./`:

	volumes:
	    - ./_src:/usr/lib/ckan/default/src

to an absolute path  to you ckan-docker directory: `/Users/username/git/ckan/ckan-docker/`

	volumes:
	    - /Users/username/git/ckan/ckan-docker/_src:/usr/lib/ckan/default/src

- Build the Docker images & run the containers:

Send the `fig up` command to the fig container

	docker exec -it fig-ckan fig up


## Using the Fig container

You can use amy fig command by pre-pending the `docker exec -it fig-ckan` command to any fig command

### build & start / recreate

	docker exec -it fig-ckan fig up

### stop it

	docker exec -it fig-ckan fig stop

### start it

	docker exec -it fig-ckan fig start

### delete the containers

	docker exec -it fig-ckan fig rm

### build new images

	docker exec -it fig-ckan fig build

### logs

	docker exec -it fig-ckan fig logs
