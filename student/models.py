from django.db import models

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.validators import RegexValidator

from datetime import datetime, date, timedelta
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager, CustomStudentManager, CustomTeacherManager, CustomClientManager, VisitManager, PaymentManager
from django.contrib.auth.models import AbstractUser
 

class CustomUser(AbstractBaseUser, PermissionsMixin):	
	phone_regex  = RegexValidator(regex=r'^0?\d{9,15}$', message="Phone number must be entered in the local format: '0XXXXXXXX'.")
	phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
	first_name   = models.CharField("first name", max_length=150, blank=True, null=True)
	last_name    = models.CharField("last name", max_length=150, blank=True, null=True)
	about	     = models.TextField("Something about you",default='', null=True, blank=True)
	avatar       = models.ImageField(blank=True, null=True, upload_to='students/', height_field=None, width_field=None)

	#Required fields
	is_staff 	  = models.BooleanField("staff", default=False, help_text="Designates wheter the user can log into this admin site")
	is_active     = models.BooleanField("active", default=True, help_text= "Designates whether this user should be treated as active. ""Unselect this instead of deleting accounts.",)
	is_client 	  = models.BooleanField("client", default=False, help_text= "Designates whether this user is client/or not",)
	date_joined   = models.DateTimeField("date joined", default=timezone.now)

	USERNAME_FIELD = 'phone_number'
	REQUIRED_FIELDS = []
	
	objects = CustomUserManager()

	class Meta:
		permissions = [
            (
                "is_client",
                "Designates if the user is client --> can go to the lessons"
            )
        ]
    # def get_absolute_url(self):
    # 	return ""

	def __str__(self):
		return self.phone_number

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

	@property
	def remained_lessons(self):
		print(f"Condition: {self.transactions.all()} , {bool(self.transactions.all())}")
		if self.transactions.all():
			transactions_list = self.transactions.all()
			untill_date 	  = transactions_list[0].untill
			lessons_remain    = transactions_list[0].numb_of_lessons
			error_lists = []
			if( len(transactions_list) == 1 and untill_date < date.today()):
				return (0, None, [])
			for i in range(1,len(transactions_list)):
				transaction_date = transactions_list[i].date_tr.date()
				if  transaction_date > untill_date:
					lessons_remain = 0
					untill_date    = None
					if transactions_list[i].type_of_tr == '-':
						error_lists.append(f"The vistit on {transactions_list[i].date_tr} was outside of the paid range") 
					else:# transactions_list[i].type_of_tr  == '+'
						lessons_remain  = transactions_list[i].numb_of_lessons
						untill_date 	= transactions_list[i].untill
				else: 
					if transactions_list[i].type_of_tr == '+':
						lessons_remain  += transactions_list[i].numb_of_lessons
						untill_date 	 = transactions_list[i].untill
					elif lessons_remain >= 1:
						lessons_remain  -= 1
					else: 
						error_lists.append(f"The vistit on {transactions_list[i].date_tr} was out of your payment")
			return (lessons_remain, untill_date, error_lists)
		return (0, None, [])	

	# def missed_lessons(self):
	# 	return list_of_missed_lessons

class Transactions(models.Model):	
	class Meta:
		db_table = 'clients_transactions'
	client			= models.ForeignKey('Client', on_delete=models.CASCADE, related_name='transactions',blank=False, null=False)
	summ 		 	= models.PositiveSmallIntegerField(default=0,blank=False, null=True)
	numb_of_lessons = models.PositiveSmallIntegerField(default=1, blank=False, null=True)
	date_tr 		= models.DateTimeField(default=timezone.now, blank=False, null=False)
	lesson			= models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE, blank=True, null=True)
	untill		 	= models.DateField(blank=True, null=True)#default=(date.now()+timedelta(month=1))
	cl_tr_id 		= models.PositiveIntegerField(blank=True, null=True, editable=False)
	type_of_tr		= models.CharField (max_length=1, choices=TypeOfTr.choices, default=TypeOfTr.PAYMENT.value, blank=False, null=False)

	def save(self, *args, **kwargs):
		self.cl_tr_id = Client.objects.tr_count(self.client.id) + 1 #Probably better to use cl_tr_id from last record ?? 
		super().save(*args, **kwargs)

	def double_visiting(self):
		all_visits = self.client.visits.all()
		lessons     = [item.lesson for item in all_visits]
		return self.lesson in lessons 
		
	def clean(self):
		tr_number 		 = Client.objects.tr_count(self.client.id)
		remained_lessons = self.client.remained_lessons[0]

		if (tr_number==0 and self.type_of_tr==TypeOfTr.VISIT.value):
			raise ValidationError("You haven't paid to access the lesson")
		if (remained_lessons==0 and self.type_of_tr==TypeOfTr.VISIT.value):
			raise ValidationError("Your remained lessons number is already 0 --> You need to extend your the subscription")
		if (self.double_visiting()):
			raise ValidationError("Double visiting the same lesson on the same time.")



class Visit(models.Model):
	objects = VisitManager()
	class Meta:
		db_table = 'clients_transactions'
		managed = False
	cl_tr_id 		= models.PositiveIntegerField(blank=True, null=True, editable=False)		
	client			= models.ForeignKey('Client', on_delete=models.CASCADE, related_name='visits')		
	# summ 		 	= models.PositiveSmallIntegerField(default=0,editable=False)
	numb_of_lessons = models.PositiveSmallIntegerField(default=1, editable=False)
	lesson			= models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE, blank=False)
	date_tr 		= models.DateTimeField(auto_now_add=True)
	# untill		 	= models.DateField(default=None, editable=False,  blank=True, null=True)
	type_of_tr		= models.CharField (max_length=1, choices=TypeOfTr.choices, default=TypeOfTr.VISIT.value, editable=False,blank=False, null=False)

	def save(self, *args, **kwargs):
		self.cl_tr_id = Client.objects.tr_count(self.client.id) + 1 #Probably better to use cl_tr_id from last record ?? 
		super().save(*args, **kwargs)
				
	def double_visiting(self):
		all_visits = self.client.visits.all()
		lessons     = [item.lesson for item in all_visits]
		return self.lesson in lessons 		

	def clean(self):
		tr_number 		 = Client.objects.tr_count(self.client.id)
		remained_lessons = self.client.remained_lessons[0]

		if (tr_number==0 and self.type_of_tr==TypeOfTr.VISIT.value):
			raise ValidationError("You haven't paid to access the lesson")
		if (remained_lessons==0 and self.type_of_tr==TypeOfTr.VISIT.value):
			raise ValidationError("Your remained lessons number is already 0 --> You need to extend your the subscription")
		if (self.double_visiting()):
			raise ValidationError("Double visiting the same lesson on the same time.")



class Payment(models.Model):
	objects = PaymentManager()
	class Meta:
		db_table = 'clients_transactions'
		managed = False
	cl_tr_id 		= models.PositiveIntegerField(blank=True, null=True, editable=False)	
	client			= models.ForeignKey('Client', on_delete=models.CASCADE, related_name='payments')
	summ 		 	= models.PositiveSmallIntegerField(default=800)	
	numb_of_lessons = models.PositiveSmallIntegerField(default=12)
	# lesson			= models.ForeignKey('lessons.Lesson', default=None,on_delete=models.CASCADE, editable=False,blank=True, null=True)
	date_tr 		= models.DateTimeField(default=timezone.now)
	untill		 	= models.DateField(blank=False)
	type_of_tr		= models.CharField (max_length=1, choices=TypeOfTr.choices, default=TypeOfTr.PAYMENT.value, editable=False, blank=False, null=False)

	def save(self, *args, **kwargs):
		self.cl_tr_id = Client.objects.tr_count(self.client.id) + 1 #Probably better to use cl_tr_id from last record ?? 
		super().save(*args, **kwargs)
		
	def clean(self):
		tr_number 		 = Client.objects.tr_count(self.client.id)
		remained_lessons = self.client.remained_lessons[0]

		if (tr_number==0 and self.type_of_tr==TypeOfTr.VISIT.value):
			raise ValidationError("You haven't paid to access the lesson")
		if (remained_lessons==0 and self.type_of_tr==TypeOfTr.VISIT.value):
			raise ValidationError("Your remained lessons number is already 0 --> You need to extend your the subscription")


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


# class CTransactions(models.Model):
# 	client			= models.ForeignKey('Client', on_delete=models.CASCADE, related_name='transaction')
# 	summ 		 	= models.PositiveSmallIntegerField(default=0)
# 	numb_of_lessons = models.PositiveSmallIntegerField(default=1)
# 	date_tr 		= models.DateTimeField()
# 	lesson			= models.ForeignKey('lessons.ActivityType', on_delete=models.CASCADE, blank=True, null=True)
# 	untill		 	= models.DateField(blank=True, null=True)#default=(date.now()+timedelta(month=1))
# 	cl_tr_id 		= models.PositiveIntegerField(blank=True, null=True, editable=False)
# 	class TypeOfTr(models.TextChoices):
# 		CHARGE 	= "+", "Payment"
# 		VISIT  	= "-", "Visit ~ -1 lesson from the account"
# 	type_of_tr		= models.CharField (max_length=9, choices=TypeOfTr.choices, default=TypeOfTr.CHARGE, blank=False, null=False)

# 	def save(self, *args, **kwargs):
# 		self.cl_tr_id = self.client.increment_tr_count()
# 		super().save(*args, **kwargs)

# 	def delete(self, *args, **kwargs):
# 		self.client.dicrement_tr_count()
# 		super().delete(*args,**kwargs)
		
# 	def clean(self):
# 		tr_number 		 = self.client.tr_count
# 		remained_lessons = self.client.remained_lessons[0]

# 		if (tr_number==0 and self.type_of_tr=="-"):
# 			raise ValidationError("You havn't paid to access the lesson")
# 		if (remained_lessons==0 and self.type_of_tr=="-"):
# 			raise ValidationError("Your remained lessons number is already 0 --> You need to extend your the subscription")

# 	def __str__(self):
# 		return f"\"{self.type_of_tr}\" #{self.id}:{self.cl_tr_id} {self.client.student_ptr.name} {self.date_tr.strftime('%d/%m/%y')}"


		

	