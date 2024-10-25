#!/bin/ash
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "Applying Migrations"
python manage.py migrate

echo "Creating Super User"
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser --username=admin --email=admin@febinosolutions.com --noinput

# echo $ENV


# exec "$@"
python manage.py load_initial_data;
# if [ "$ENV" = 'production' ]; 
# then 
#   echo 'Initialing Server Data' &&  
# else 
#   echo 'Initialing Local Datas' && python manage.py loaddata initial_local_data.json; 
# fi 

python manage.py runserver 0.0.0.0:8000 --noreload