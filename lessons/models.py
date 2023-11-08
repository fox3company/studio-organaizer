from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.validators import RegexValidator
from datetime import datetime, date, timedelta, time
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.exceptions import ValidationError
from users.models import Client
# from student.models import Student, Client


class Location(models.Model):
	name		= models.CharField(max_length=35, default="The Space project[Center]", blank=False, null=False)
	url_name	= models.CharField(max_length=35, editable=False, blank=True, null=False )
	photo 	= models.ImageField(upload_to='locations/',height_field=None, width_field=None, blank=True, null=True)
	about	= models.TextField(blank=True, null=True)
	geo 	= models.URLField(default="https://goo.gl/maps/HZwWj15NgYrt2vBz9", blank=False, null=False)
	def save(self, *args, **kwargs):
		if self._state.adding == True:
			self.url_name = self.name.casefold().replace(" ","_")
		super().save(*args, **kwargs)
	def __str__(self):
		return self.name

class Studio(models.Model):
	number 	     = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=8, blank=False, null=False)
	photo 		 = models.ImageField(upload_to='locations/studios/',height_field=None, width_field=None, blank=True, null=True)
	about		 = models.TextField(blank=True, null=True)
	geo_location = models.ForeignKey('Location', related_name='studios', on_delete=models.CASCADE, blank=False, null=False)

	def __str__(self):
		return f"{self.geo_location.name}: Studio №{str(self.number)} "

class ActivityType(models.Model):
	activity_name = models.CharField(max_length=35, default="Contemporary Dance", blank=False, null=False)
	about		  = models.TextField(blank=True, null=True)
	more 		  = models.URLField(blank=True, null=True)
	meadia_repr   = models.ImageField(upload_to='activities/',height_field=None, width_field=None, blank=True, null=True)


	def __str__(self):
		return self.activity_name

class Lesson(models.Model):
	class Meta:
		ordering = ['start_date','start_time','end_at']
		# unique_together = [['activity', 'start_date', 'studio']]
		# constraints = [ models.UniqueConstraint(fields=['activity','studio','start_date']), name='lesson_is_unique' ]
#General Info
	activity 	= models.ForeignKey('ActivityType', on_delete=models.CASCADE, blank=False, null=False) 
	teacher		= models.ForeignKey('users.Teacher', on_delete=models.CASCADE, blank=False, null=False)
	quantity	= models.PositiveSmallIntegerField(default=12, validators=[MaxValueValidator(35)], blank=False, null=False) #For that specifix version, iw would be no more than 35 people per room
	clients	    = models.ManyToManyField('users.Client', related_name='lessons', blank=True)
	queue 		= models.ManyToManyField('users.Client', related_name='+', blank=True)
	#q_of_registred_users = property 
#All information date and time
	start_date  = models.DateField(blank=False, null=False)
	start_time  = models.TimeField(blank=False, null=False)#timezone.now().strftime("%H:%M:%S") 
	# duration 	= start_date - end_at
	end_at 		= models.TimeField(blank=False, null=False)#time(hour=timezone.now().hour+2,minute=timezone.now().minute,second=timezone.now().second 

#All about the place
	studio  	= models.ForeignKey('Studio',on_delete=models.CASCADE, blank=False, null=False)
	#approved = boolean

	@property
	def duration(self):	
		def strfdelta(tdelta):
			d = {"hours":0, "minutes":0, "seconds":0}
			d["hours"],   rem 		   = divmod(tdelta.seconds, 3600)
			d["minutes"], d["seconds"] = divmod(rem, 60)
			tdelta_to_time = time(hour=d['hours'],minute=d['minutes'],second=d['seconds'])
			return tdelta_to_time.isoformat(timespec="minutes")

		starting = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute, seconds= self.start_time.second)
		ending 	 = timedelta(hours=self.end_at.hour, minutes=self.end_at.minute, seconds= self.end_at.second)
		delta = ending - starting
		return strfdelta(delta)

	@property
	def q_of_registred_users(self):
		return self.clients.count()

	def check_cancelation_possibility(self):
		datetime_start =  datetime.combine(self.start_date, self.start_time)
		datetime_now   = datetime.now()
		delta = datetime_start - datetime_now
		response = False
		if delta.days > 0:
			response = True
		if delta.seconds > 8*60*60:
			response = True
		return response

	def check_client_registration(self, client_id):
		client = get_object_or_404(Client,pk=client_id)
		response = True if client in self.clients.all() else False 
		return response

	def check_client_in_queue(self, client_id):
		client = get_object_or_404(Client,pk=client_id)
		response = True if client in self.queue.all() else False 
		return response

	# @property
	# def end_at(self):
	# 	timeList 	= [self.start_time, self.duration]
	# 	ending_time = datetime.timedelta() 
	# 	for i in timeList:
	# 	    (h, m, s) = (i.hour, i.minute, i.second)
	# 	    d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
	# 	    ending_time += d
	# 	return ending_time 

	def __str__(self):
		activity 		= self.activity.activity_name
		when_date    	= self.start_date.strftime("%d %B")
		day_of_the_week = self.start_date.strftime("%A")
		when_hour		= self.start_time.strftime("%H:%M")
		return f"#{self.id} {activity}: {when_date} {day_of_the_week} at {when_hour}"