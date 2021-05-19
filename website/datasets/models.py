from django.db import models

# Create your models here.

class Dataset(models.Model):
	name = models.CharField(max_length = 200)
	channel_no = models.IntegerField(default = 3)
	shutter_speed = models.FloatField(default = 1)
	no_of_photos = models.IntegerField(default = 0)
	def __str__(self):
		return self.name

class Photo(models.Model):
	dataset = models.ForeignKey(Dataset, on_delete = models.CASCADE)
	# some other atributes

