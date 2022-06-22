from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.validators import RegexValidator


class Location(models.Model):
	name	= models.CharField(max_length=35, default="The Space project[Center]")
	geo 	= models.URLField(default="https://goo.gl/maps/HZwWj15NgYrt2vBz9")

	def __str__(self):
		return self.name

class Studio(models.Model):
	number 	     = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=8)
	geo_location = models.ForeignKey('Location', on_delete=models.CASCADE)

	def __str__(self):
		return str(self.number)

class Lesson(models.Model):
#General Info
	name 		= models.CharField(max_length=35) 
	about		= models.TextField()
	meadia_repr = models.ImageField(upload_to='lessons/',height_field=None, width_field=None)
	teacher		= models.ForeignKey('teacher.Teacher', on_delete=models.CASCADE)
	quantity	= models.PositiveSmallIntegerField(default=25, validators=[MaxValueValidator(35)]) #For that specifix version, iw would be no more than 35 people per room

#All information about, when lesson would be	
	start_date  = models.DateField()
	start_time  = models.TimeField() 
	duration 	= models.TimeField()
	#end_at 	= time //For that version, ending is always on the same day. The studio doesn't support long events yet.
# Where, lesson would be
	studio  	= models.ForeignKey('Studio',on_delete=models.CASCADE)
	#approved = boolean

	@property
	def end_at(self):
		timeList 	= [self.start_time, self.duration]
		ending_time = datetime.timedelta() 
		for i in timeList:
		    (h, m, s) = (i.hour, i.minute, i.second)
		    d = datetime.timedelta(hours=int(h), minutes=int(m), seconds=int(s))
		    ending_time += d
		return ending_time 

	def __str__(self):
		return self.name


class Student(models.Model):
	name 	 	 = models.CharField(max_length=35)
	about	 	 = models.TextField(default='')
	avatar   	 = models.ImageField(blank=True, upload_to='students/', height_field=None, width_field=None)
	phone_regex  = RegexValidator(regex=r'^0?\d{9,15}$', message="Phone number must be entered in the local format: '0XXXXXXXX'.")
	phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)

	def __str__(self):
		return self.name


	