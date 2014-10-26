Fig
===

The Fig container runs Fig version 1.0 & the latest Docker within a container.

# Usage:

The Docker socket needs to be mounted as a volume to control Docker on the host. A source folder must be mounted to access the fig definition


## Build & Run

_from your root directory of the project_

Build it:

	docker build --tag="fig_container" docker/fig

Run it:

	docker run -it -d --name="fig-cli" -p 2375 -v /var/run/docker.sock:/tmp/docker.sock -v $(pwd):/src fig_container

set the source volume path to yours

## Using the Fig container

### bring it back up

	docker exec -it fig-cli fig up

### stop it

	docker exec -it fig-cli fig stop

### delete the containers

	docker exec -it fig-cli fig rm

### build new images

	docker exec -it fig-cli fig build
