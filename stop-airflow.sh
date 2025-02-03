echo "Stopping airflow"
pkill -f "airflow scheduler"
pkill -f "airflow webserver"
