# Docker Compose setup for DBCA CKAN

## Install Dependencies
- docker
- git
- ahoy (https://github.com/ahoy-cli/ahoy)

## Configure extensions that will be worked on
 - Add any extensions you will be modifying in the file `src/dbca_install_extensions.sh`

## Init and build local dev environment
- ahoy init
  - This will clone the extensions from `dbca_install_extensions.sh` to the `src` folder which will be a mounted folder to the ckan docker containers
  - Copy the `.env.dbca` to `.env` which is the env file uses for the CKAN docker containers
    - Update the `.env` file to. The extension https://github.com/okfn/ckanext-envvars reads this file on CKAN startup and require to be in a certain format. Please read the readme file https://github.com/okfn/ckanext-envvars#ckanext-envvars
      - Enable plugins via `CKAN__PLUGINS`
      - Add/Update CKAN core configuration values
      - Add/Update CKAN extensions configuration values
      - Any updates to this file will recreate the container service to use the updates values when `ahoy up` is used
- ahoy build (Build the projects docker images)
- ahoy up (Starts the projects container services)
  - The first time the CKAN Dev containers are created the mapped volume will look in the `src:/srv/app/src_extensions` folder to install any extensions cloned from the `ahoy init` step and will pip install the extension and any any requirements file if they exists
- To see the list of available commands with short descriptions run ahoy
```
ahoy      
NAME:
   ahoy - Creates a configurable cli app for running commands.
USAGE:
   ahoy [global options] command [command options] [arguments...]
   
COMMANDS:
   attach              Attach to a running container
   build               Build project.
   cli                 Start a shell inside container.
   db-dump             Dump data out into a file. `ahoy db-dump local.dump`
   db-import           Pipe in a postgres dump file.  `ahoy db-import local.dump`
   down                Delete project (CAUTION).
   generate-extension  Generates a new CKAN extension into the src directory
   info                Print information about this project.
   init                Initialise the codebase on first-time setup (ahoy init)
   logs                Show Docker logs.
   open                Open the site in your default browser
   ps                  List running Docker containers.
   recreate            Recreate a local container | ahoy recreate ckan
   restart             Restart Docker containers.
   run                 Run command inside container.
   stop                Stop Docker containers.
   up                  Build project.

GLOBAL OPTIONS:
   --verbose, -v               Output extra details like the commands to be run. [$AHOY_VERBOSE]
   --file value, -f value      Use a specific ahoy file.
   --help, -h                  show help
   --version                   print the version
   --generate-bash-completion  
   
VERSION:
   2.0.2-homebrew
   
[fatal] Missing flag or argument.```