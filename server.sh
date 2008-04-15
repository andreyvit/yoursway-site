#!/bin/bash

# Replace these three settings.
PROJDIR="$PWD"
PIDFILE="$PROJDIR/site.pid"

case "$1" in 
	start)
		if [ ! -f $PIDFILE ]; then

		    sudo su buriy -c "PYTHONPATH="$PROJDIR" \
                        python $PROJDIR/manage.py runfcgi pidfile=$PIDFILE \
                         socket=$PROJDIR/site.sock daemonize=true method=threaded"
                    echo "Server started."
		else
		    echo "Warning: PID file exists!"
		fi
                ;;
	stop)
		if [ -f $PIDFILE ]; then
                    PROCESS=`cat -- $PIDFILE`
		    sudo su buriy -c "kill -9 $PROCESS"
		    sudo su buriy -c "rm $PIDFILE"
                    echo "Server stopped."
		fi

		;;

	up)
		if ! [[ `pgrep -lf "python $PROJDIR/manage.py runfcgi"` ]]; then
		    $PROJDIR/$0 start
		fi;
    
		;;

	restart)
		$PROJDIR/$0 stop
		$PROJDIR/$0 start
		;;
	*)
		echo "Usage: $0 start|stop|restart"
		;;
esac
