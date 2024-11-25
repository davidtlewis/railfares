

#Getting the data from National Rail

get the token:
     curl 'https://opendata.nationalrail.co.uk/authenticate' \
     --data-urlencode 'username=david.lewis@itoworld.com' \
     --data-urlencode 'password=[password]'

curl 'https://opendata.nationalrail.co.uk/authenticate' --data-urlencode 'username=david.lewis@itoworld.com' --data-urlencode 'password=Mervansep123!'

 
curl 'https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/fares' \
-H 'X-Auth-Token: [token]]' \
--output fares.zip
 
 
curl 'https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/routeing' \
-H 'X-Auth-Token: [token]' \
--output routeing.zip
 
#Importing files into the django app

Locations
python manage.py import_locations ../raildata/***.LOC
239k records - but most ignored - only those with enddates > 2024 processed

Clusters
python manage.py import_clusters ../raildata/***.FSC
40k takes a few minutes

Ticket Types
python manage.py import_tickettypes ../raildata/***.TTY
quick

Flows File
python manage.py import_flows ../raildata/***.FFL
706k flow records

python manage.py import_fares ../raildata/***.FFL
7 million fare records!



Working views
simple search for fares from station A to Station B
http://127.0.0.1:8000/find_fares/?origin=0785&destination=1900

Form based search - includes station and clusters
http://127.0.0.1:8000/find_fares_view/


Fare.objects.all().delete()
Flow.objects.all().delete()
StationCluster.objects.all().delete()
StationGroup.objects.all().delete()
Station.objects.all().delete()



python3 manage.py import_locations ../raildata/RJFAF217.LOC
python3 manage.py import_clusters ../raildata/RJFAF217.FSC
python3 manage.py import_flows ../raildata/RJFAF217.FFL

TODO - need to fix location importer to fix up the nlc code for groups - in the meantime....

for group in StationGroup.objects.all():
     group.save()

