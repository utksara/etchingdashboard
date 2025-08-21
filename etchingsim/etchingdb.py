from django.db import models
import json

class EtchingData(models.Model):
    name = models.CharField(max_length=255)
    hashed_data = models.JSONField()
    

etching_data = json.load("etching_db.json")

# Creating the object in Django
etching_obj = EtchingData.objects.create(
    name="Hashed Points with Scalars",
    hashed_data=etching_data
)