from django.db import models
# from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.validators import RegexValidator
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned,SuspiciousOperation

from datetime import datetime, date, timedelta
from django.utils import timezone

from django.shortcuts import get_object_or_404


from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager, CustomStudentManager, CustomTeacherManager, CustomClientManager
 

now   = timezone.now()
today = timezone.localtime(now).date()


class CustomUser(AbstractBaseUser, PermissionsMixin):	
	phone_regex  = RegexValidator(regex=r'^0?\d{9,15}$', message="Phone number must be entered in the local format: '0XXXXXXXX'.")
	phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True, blank=False, null=False)
	first_name   = models.CharField("first name", max_length=150, blank=True, null=True)
	last_name    = models.CharField("last name", max_length=150, blank=True, null=True)
	about	     = models.TextField("Something about you",default='', null=True, blank=True)
	avatar       = models.ImageField(blank=True, null=True, upload_to='students/', height_field=None, width_field=None)
	sexType 	 = models.TextChoices('sexlType', 'M F')
	sex 		 = models.CharField(choices=sexType.choices, max_length=1, blank=True, null=True)

	visits_count   		= models.PositiveIntegerField(default=0, editable=False, blank=False, null=False)
	payments_count  	= models.PositiveIntegerField(default=0, editable=False, blank=False, null=False)	
	active_subscription = models.OneToOneField('activities.Payment' ,on_delete=models.CASCADE, blank=True, null=True, related_name='user_client')
	
	#Required fields
	is_staff 	  = models.BooleanField("staff", default=False, help_text="Designates wheter the user can log into this admin site")
	is_teacher	  = models.BooleanField("teacher", default=False, help_text="Designates wheter the user is a teacher")
	is_active     = models.BooleanField("active", default=True, help_text= "Designates whether this user should be treated as active. ""Unselect this instead of deleting accounts.",)
	is_client 	  = models.BooleanField("client", default=False, help_text= "Designates whether this user is client/or not",)
	date_joined   = models.DateTimeField("date joined", auto_now_add=True)

	USERNAME_FIELD = 'phone_number'
	REQUIRED_FIELDS = []
	
	objects = CustomUserManager()

	class Meta:
		permissions = [
			(
				"is_client",
				"Designates if the user is client --> can go to the lessons"
			),
			(
				"is_teacher",
				"Designates wheter the user is a teacher"
			)
		]

	# def get_absolute_url(self):
	# 	return ""

	def __str__(self):
		return self.phone_number

	def to_client(self):
		client = get_object_or_404(Client,id=self.id)
		return client

	def to_student(self):
		student = get_object_or_404(Student,id=self.id)
		return student


class Teacher(CustomUser):
	objects = CustomTeacherManager()
	class Meta:
		proxy = True

class Student(CustomUser):
	objects = CustomStudentManager()
	class Meta:
		proxy = True

class Client(CustomUser):
	objects = CustomClientManager()
	class Meta:
		proxy = True

	def deactivate_unvalid_subscr(self):
		if self.active_subscription:
			if self.active_subscription.subs_is_valid_for_today():	
				raise SuspiciousOperation("You've tried to delete a valid subsciption")	
			self.active_subscription.is_active = False
			self.active_subscription.save()
			self.active_subscription = None
			self.save()
		else:
			ObjectDoesNotExist("It raised during deactivating unvalid subsciption")

	def check_if_exist_other_subsc(self): #and activate
		other_valid_subscr = self.payments.all().filter(untill_date__gte=today).filter(from_date__lte=today).filter(remains_lessons__gte=1).order_by('timestamp')
		if other_valid_subscr.count() > 0:
			new_subs = other_valid_subscr[0]
			new_subs.is_active = True
			new_subs.save()
			return True 
		else:
			return False

	def check_if_subs_exist(self):
		now_subs_exist = self.active_subscription
		if now_subs_exist:
			if self.active_subscription.subs_is_valid_for_today():
				return True
			self.deactivate_unvalid_subscr()
		other_valid_subs_exist = self.check_if_exist_other_subsc()
		if other_valid_subs_exist:
			return True
		else:
			return False

	def active_subs_validation(self):
		if self.active_subscription:
			if self.active_subscription.subs_is_valid_for_today():
				return True
			return False
		else: 
			return None

	def remained_lessons(self):#only for the view
		if self.active_subscription:
			if self.active_subscription.from_date <= today and today <= self.active_subscription.untill_date:
				return self.active_subscription.remains_lessons
			else: 
				return 0
		else: 
			ObjectDoesNotExist("It raised during accessing client's active subsription")

	def missed_lessons(self):
		qs_lessons = list(self.lessons.all().filter(start_date__lt=today))	
		plus_today_missed_lessons = list(self.lessons.all().filter(start_date=today).filter(end_at__lte=now))

		qs_lessons.extend(plus_today_missed_lessons)
		qs_lessons.sort(key=lambda lesson:lesson.start_date)

		qs_visits  = list(self.visits.all())
		for visit in qs_visits:
			if visit.lesson in qs_lessons:
				qs_lessons.remove(visit.lesson)
		list_of_missed_lessons=qs_lessons 
		return list_of_missed_lessons

	def with_us(self):
		all_payments = self.payments.all()
		with_us_month = 0
		for payment in all_payments:
			duration = (payment.untill_date - payment.from_date)
			if timedelta(days=28) <= duration and duration <= timedelta(days=37):
				with_us_month += 1 
			else: 
				with_us_month = with_us_month + duration.days//30 
		return with_us_month 


	# def remained_lessons(self, new_tr): Misses the following: payment[April,May],payment[July, August] --> [May, June] one can't visit the Studio
	# 	if self.transactions.all():
	# 		transactions_list = self.transactions.all()
	# 		start_date 	  	  = [transactions_list[0].date_tr.date(),]
	# 		strd_i 			  = 0
	# 		untill_date 	  = [transactions_list[0].untill,]
	# 		untd_i 			  = 0
	# 		lessons_remain    = transactions_list[0].numb_of_lessons
	# 		error_lists = []
	# 		if( len(transactions_list) == 1 and untill_date[untd_i] < new_tr.date_tr.date()):
	# 			return (0, None, [])
	# 		for i in range(1,len(transactions_list)):
	# 			transaction_date = transactions_list[i].date_tr.date()
	# 			if  transaction_date > untill_date[untd_i]:
	# 				lessons_remain = 0
	# 				untill_date[untd_i] = None
	# 				start_date[strd_i]  = None
	# 				if transactions_list[i].type_of_tr == '-':
	# 					error_lists.append(f"The vistit on {transactions_list[i].date_tr} was outside of the paid range") 
	# 				else:# transactions_list[i].type_of_tr  == '+'
	# 					lessons_remain     = transactions_list[i].numb_of_lessons
	# 					untill_date[untd_i]= transactions_list[i].untill
	# 					start_date[strd_i] = transactions_list[i].date_tr.date()
	# 			else:# transaction_date <= untill_date[untd_i]
	# 				if transactions_list[i].type_of_tr == '+':
	# 					lessons_remain += transactions_list[i].numb_of_lessons
	# 					untill_date.append(transactions_list[i].untill)
	# 					untd_i += 1
	# 					start_date.append(transactions_list[i].date_tr.date())
	# 					strd_i += 1
	# 				else:# transactions_list[i].type_of_tr == '-' and transaction_date <= untill_date[untd_i]
	# 					if transaction_date >= start_date[strd_i]:
	# 						if  lessons_remain >= 1:
	# 							lessons_remain  -= 1
	# 						else: 
	# 							error_lists.append(f"The vistit on {transactions_list[i].date_tr} was out of your payment")
	# 					else:# type '-' and transaction_date <= untill_date[untd_i] and transaction_date < start_date[strd_i]
	# 						try:
	# 							j = -1 if untd_i == 0 else untd_i
	# 							if transaction_date > untill_date[j-1]:
	# 								error_lists.append(f"The vistit on {transactions_list[i].date_tr} was out of paid period")
	# 							else:# transaction_date <= untill_date[untd_i-1]
	# 								if  lessons_remain >= 1:
	# 									lessons_remain  -= 1
	# 								else: 
	# 									error_lists.append(f"The vistit on {transactions_list[i].date_tr} was out of your payment")
	# 						except IndexError:# untill_date[untd_i-1] doesn't exist
	# 							if  lessons_remain >= 1:
	# 									lessons_remain  -= 1
	# 							error_lists.append(f"The vistit on {transactions_list[i].date_tr} was out of paid period") 
	# 		if new_tr.type_of_tr == '-':
	# 			if new_tr.date_tr.date() > untill_date[untd_i]:
	# 				return (0, None, [])
	# 			if new_tr.date_tr.date() < start_date[strd_i]:
	# 				try:
	# 					j = -1 if untd_i == 0 else untd_i
	# 					if new_tr.date_tr.date() <= untill_date[j-1]:
	# 						return (lessons_remain, untill_date[untd_i], error_lists)	
	# 				except IndexError:
	# 					return (0, None, [])
	# 		return (lessons_remain, untill_date[untd_i], error_lists)
	# 	return (0, None, [])	

 # class Student(models.Model):
	# name 	 	 = models.CharField(max_length=35)
	# about	 	 = models.TextField(default='')
	# avatar   	 = models.ImageField(blank=True, upload_to='students/', height_field=None, width_field=None)
	# phone_regex  = RegexValidator(regex=r'^0?\d{9,15}$', message="Phone number must be entered in the local format: '0XXXXXXXX'.")
	# phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)

	# def __str__(self):
	# 	return self.name

# class Client(models.Model):
# 	student_ptr = models.OneToOneField('Student', on_delete=models.CASCADE, related_name='client')
# 	tr_count 	= models.PositiveIntegerField(default=0, editable=False)   

# 	@property
# 	def expiration_date(self):
# 		return self.transaction.untill 
# 	@property
# 	def remained_lessons(self):
# 		if self.transaction.all():
# 			transactions_list = self.transaction.all()

# 			untill_date 	= transactions_list[0].untill
# 			lessons_remain  = transactions_list[0].numb_of_lessons
# 			error_lists = []

# 			for i in range(1,len(transactions_list)):
# 				transaction_date = transactions_list[i].date_tr.date()
# 				if  transaction_date > untill_date:
# 					lessons_remain = 0
# 					untill_date    = None
# 					if transactions_list[i].type_of_tr == '-':
# 						error_lists += f"The vistit on {transactions_list[i].date_tr} was outside of the paid range" 
# 					else:# transactions_list[i].type_of_tr  == '+'
# 						lessons_remain  = transactions_list[i].numb_of_lessons
# 						untill_date 	= transactions_list[i].untill
# 				else: 
# 					if transactions_list[i].type_of_tr == '+':
# 						lessons_remain  += transactions_list[i].numb_of_lessons
# 						untill_date 	+= transactions_list[i].untill
# 					elif lessons_remain >= 1:
# 						lessons_remain  -= transactions_list[i].numb_of_lessons
# 					else: 
# 						error_lists += f"The vistit on {transactions_list[i].date_tr} was out of your payment"
# 			return (lessons_remain, untill_date, error_lists)
# 		return (0, None, [])	

# 	def increment_tr_count(self):
# 		self.tr_count += 1
# 		self.save()
# 		return self.tr_count

# 	def dicrement_tr_count(self):
# 		self.tr_count -= 1
# 		self.save()
# 		return self.tr_count


# 	def __str__(self):
# 		return f"{self.student_ptr.first_name} {self.student_ptr.last_name}: {self.student_ptr.phone_number}"#


		

	