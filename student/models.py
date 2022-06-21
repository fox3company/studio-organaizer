from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.


class Lesson(models.Model):
#General Info
	name 		= models.CharField(max_length=35) 
	about		= models.TextField()
	meadia_repr = models.ImageField(upload_to='lessons/',height_field=None, width_field=None)
	#teacher		= models.ForeignKey('teacher.Teacher', on_delete=models.CASCADE)
	quantity	= models.PositiveSmallIntegerField(default=25, validators=[MaxValueValidator(35)])

#All information about, where lesson would be	
	start_date  = models.DateField()
	start_time  = models.TimeField() 
	duration 	= models.TimeField()
	#end_at 	= time //For that version, ending is always on the same day. The studio doesn't support long events yet.

#All information about, where lesson would be
	loaction 	= models.URLField(default="https://goo.gl/maps/HZwWj15NgYrt2vBz9")
	studios  	= [
		(101,'Studio №=101'),
		(109,'Studio №=109'),
		(115,'Studio №=115'),
		(201,'Studio №=201'),
		(205,'Studio №=205'),
		(208,'Studio №=208'),
	]
	studio_numb = models.IntegerField(choices=studios)
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





	