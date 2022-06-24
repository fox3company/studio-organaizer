from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.validators import RegexValidator
from datetime import datetime, date, timedelta
from django.utils import timezone


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

class ActivityType(models.Model):
	activity_name = models.CharField(max_length=35, default="Contempory Dance")
	about		  = models.TextField()
	meadia_repr   = models.ImageField(upload_to='activities/',height_field=None, width_field=None)

	def __str__(self):
		return self.activity_name

class Lesson(models.Model):
#General Info
	activity 	= models.ForeignKey('ActivityType', on_delete=models.CASCADE) 
	teacher		= models.ForeignKey('teacher.Teacher', on_delete=models.CASCADE)
	quantity	= models.PositiveSmallIntegerField(default=25, validators=[MaxValueValidator(35)]) #For that specifix version, iw would be no more than 35 people per room

#All information date and time
	start_date  = models.DateField()
	start_time  = models.TimeField() 
	duration 	= models.TimeField()
	#end_at 	= time //For that version, ending is always on the same day. The studio doesn't support long events yet.

#All about the place
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
		activity 		= self.activity.activity_name
		when_date    	= self.start_date.strftime("%d %B")
		day_of_the_week = self.start_date.strftime("%A")
		when_hour		= self.start_time.strftime("%H:%M")
		return f"{activity}: {when_date} {day_of_the_week} at {when_hour}"


class Student(models.Model):
	name 	 	 = models.CharField(max_length=35)
	about	 	 = models.TextField(default='')
	avatar   	 = models.ImageField(blank=True, upload_to='students/', height_field=None, width_field=None)
	phone_regex  = RegexValidator(regex=r'^0?\d{9,15}$', message="Phone number must be entered in the local format: '0XXXXXXXX'.")
	phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)

	def __str__(self):
		return self.name

class Client(models.Model):
	student_ptr = models.OneToOneField('Student', on_delete=models.CASCADE, related_name='client')
	
	@property
	def expiration_date(self):
		return self.transaction.untill 
	@property
	def remained_lessons(self):
		transactions_list = self.transaction.all()
		# if transactions_list[0] != '+'
		# 	error

		untill_date 	= transactions_list[0].untill
		lessons_remain  = transactions_list[0].numb_of_lessons
		error_lists = []

		for i in range(1,len(transactions_list)):
			transaction_date = transactions_list[i].date_tr.date()
			if  transaction_date > untill_date:
				lessons_remain = 0
				untill_date    = None
				if transactions_list[i].type_of_tr == '-':
					error_lists += f"The vistit on {transactions_list[i].date_tr} was outside of the paid range" 
				else:# transactions_list[i].type_of_tr  == '+'
					lessons_remain  = transactions_list[i].numb_of_lessons
					untill_date 	= transactions_list[i].untill
			else: 
				if transactions_list[i].type_of_tr == '+':
					lessons_remain  += transactions_list[i].numb_of_lessons
					untill_date 	+= transactions_list[i].untill
				elif lessons_remain >= 1:
					lessons_remain  -= 1
				else: 
					error_lists += f"The vistit on {transactions_list[i].date_tr} was out of your payment"
		return (lessons_remain, untill_date, error_lists)	

	def __str__(self):
		return self.student_ptr.name


class CTransactions(models.Model):
	client			= models.ForeignKey('Client', on_delete=models.CASCADE, related_name='transaction')
	summ 		 	= models.PositiveSmallIntegerField(default=0)
	numb_of_lessons = models.PositiveSmallIntegerField(default=1)
	date_tr 		= models.DateTimeField()
	lesson			= models.ForeignKey('ActivityType', on_delete=models.CASCADE, blank=True, null=True)
	untill		 	= models.DateField(blank=True, null=True)#default=(date.now()+timedelta(month=1))
	
	class TypeOfTr(models.TextChoices):
		CHARGE 	= "+", "Payment"
		VISIT  	= "-", "Visit ~ -1 lesson from the account"
	type_of_tr		= models.CharField (max_length=9, choices=TypeOfTr.choices, default=TypeOfTr.CHARGE, blank=False, null=False)


	