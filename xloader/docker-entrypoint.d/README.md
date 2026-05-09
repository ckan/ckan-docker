Use scripts in this folder to run extra initialization steps in your custom CKAN images.
Any file with `.sh` or `.py` extension will be executed just after the main initialization
script (`prerun.py`) is executed and just before the web server and supervisor processes are
started.
