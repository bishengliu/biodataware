#! /bin/bash
# this is the config for biodataware

NAME="biodataware"                              #Name of the application (*)
DJANGODIR=/var/www/html/biodataware/biodataware             # Django project directory (*)
SOCKFILE=/var/www/html/biodataware/run/gunicorn.sock        # we will communicate using this unix socket
USER=bioku                                        # the user to run as (*)
GROUP=bioku                                     # the group to run as (*)
NUM_WORKERS=1                                     #  how many worker processes should Gunicorn spawn (*)
DJANGO_SETTINGS_MODULE=config.settings.test       # which settings file should Django use (*)
DJANGO_WSGI_MODULE=config.wsgi_test                     # WSGI module name (*)

echo "Starting $NAME as `whoami`, the server must be run by user: $USER !"

# Activate the virtual environment
cd $DJANGODIR
source /var/www/html/biodataware/biodatawareenv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
#   
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /usr/local/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user $USER \
  --bind=unix:$SOCKFILE