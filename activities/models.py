from django.db import models
from django.core.exceptions import ValidationError
from users.models import Client, Student

from datetime import datetime, date, timedelta
from django.utils import timezone

# Create your models here.

now   = timezone.now()
today = timezone.localtime(now).date()


class Payment(models.Model):#Payments
	cl_pay_id 		= models.PositiveIntegerField(blank=True, editable=False)	
	client			= models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='payments', blank=False, null=False)
	
	is_active 	    = models.BooleanField(default=False, blank=False, null=False)

	comments 		= models.TextField("Additional comments",default='', null=True, blank=True)
	summ 		 	= models.PositiveSmallIntegerField(default=800, blank=False, null=False)	
	# date_tr 		= models.DateTimeField(default=timezone.now)#?????????
	from_date       = models.DateField(blank=False, null=False)
	untill_date		= models.DateField(blank=False, null=False)
	remains_lessons = models.PositiveSmallIntegerField(editable=False, blank=True, null=False)
	buied_lessons   = models.PositiveSmallIntegerField(default=12, blank=False, null=False)
	lessons         = models.ManyToManyField('lessons.Lesson', related_name='+', editable=False, blank=True)
	class CurrencyType(models.TextChoices):
		MDL = 'MDL', "MDL"
		EUR = 'EUR', "EUR"
		USD = 'USD', "USD"
	currency  = models.CharField(choices=CurrencyType.choices, default=CurrencyType.MDL.value, max_length=10)

	timestamp 		= models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		paid_in_time = False
		state = self._state.adding

		if state == True:
			self.client.payments_count = self.client.payments_count + 1
			self.cl_pay_id 	= self.client.payments_count
			self.remains_lessons = self.buied_lessons 

			now_subs_exist = self.client.active_subscription	
			
			if now_subs_exist: 
				if today <= now_subs_exist.untill_date and (now_subs_exist.untill_date + timedelta(days=1)) == self.from_date:
					self.remains_lessons += self.client.active_subscription.remains_lessons
					self.client.active_subscription.remains_lessons = 0
					self.client.active_subscription.untill_date  	= (today - timedelta(days=1))
					self.client.active_subscription.is_active 		= False 
					self.client.active_subscription.comments 		= f"All remaining lessons&days from that subscription moved to the next one {self}"
					self.from_date = today
					self.is_active = True
					paid_in_time = True
					self.client.active_subscription.save()
		super().save(*args, **kwargs)

		bool_flag = False 
		if paid_in_time:
			self.client.active_subscription = None
			self.client.active_subscription = self
		else:
			if self.is_active == True and self.client.active_subscription != self:
				if self.client.active_subscription.subs_is_valid_for_today():
					pass
				else: 
					self.client.active_subscription = self
					bool_flag = True

		if state or bool_flag:
			self.client.save()

	def clean(self):
		if self.client.active_subs_validation() == True and self.is_active == True and self != self.client.active_subscription:
			raise ValidationError("You can't add two valid active subsription")

	# def delete(self, *args, **kwargs):
	# 	self.client.payments_count = self.client.payments_count - 1
	# 	self.client.save()
	# 	super().delete(*args,**kwargs)


	def subs_is_valid_for_today(self):
		today_in_subsc_range = True if self.from_date <= today and today <= self.untill_date else False 
		if_remains_lessons   = True if self.remains_lessons >= 1 else False  
		boll_response = today_in_subsc_range and if_remains_lessons
		return boll_response

	def __str__(self):
		return  f"#{self.client}. {self.from_date} - {self.untill_date} = {self.buied_lessons} lessons/remains [{self.remains_lessons}] ||| is_active: {self.is_active}"

class Visit(models.Model):
	cl_v_id 		= models.PositiveIntegerField(blank=True, null=False, editable=False)		
	client			= models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='visits', blank=False, null=False)		

	lesson			= models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE, blank=False, null=False)
	timestamp 		= models.DateTimeField(auto_now_add=True, blank=False, null=False)

	def double_visiting(self):
		all_visits = self.client.visits.all()
		lessons     = [item.lesson for item in all_visits]
		return self.lesson in lessons

	def save(self, *args, **kwargs):
		if self._state.adding == True:
			self.client.visits_count = self.client.visits_count + 1
			self.client.save()
			self.cl_v_id = self.client.visits_count
		super().save(*args, **kwargs)

	# def delete(self, *args, **kwargs):
	# 	self.client.visits_count = self.client.visits_count - 1
	# 	self.client.save()
	# 	super().delete(*args,**kwargs)

	def clean(self):
		# if self.client.check_if_subs_exist():
		# 	if self.client.remained_lessons() > 0:
		# 		self.client.active_subscription.remains_lessons -= 1	
		# 	else:
		# 		self.client.deactivate_unvalid_subscr()
		# 		raise ValidationError("You need to extend your subscritions.")
		# else:
		# 	raise ValidationError("Your visit is out of paied boundaries.")
		if self.client not in self.lesson.clients.all():
			raise ValidationError("You can't visit the lesson, because you haven't registred to it")

		if (self.double_visiting()):
			raise ValidationError("Double visiting the same lesson on the same time.")

	def __str__(self):
		return f"@Visit: {self.lesson} by user {self.client}" #{self.timestamp.strftime('%d/%m/%y')}



# class Transactions(models.Model):	
# 	class Meta:
# 		db_table = 'clients_transactions'
# 	client			= models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='transactions',blank=False, null=False)
# 	summ 		 	= models.PositiveSmallIntegerField(default=0,blank=False, null=True)
# 	numb_of_lessons = models.PositiveSmallIntegerField(default=1, blank=False, null=True)
# 	date_tr 		= models.DateTimeField(default=timezone.now, blank=False, null=False)
# 	lesson			= models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE, blank=True, null=True)
# 	untill		 	= models.DateField(blank=True, null=True)#default=(date.now()+timedelta(month=1))
# 	cl_tr_id 		= models.PositiveIntegerField(blank=True, null=True, editable=False)
# 	type_of_tr		= models.CharField (max_length=1, choices=TypeOfTr.choices, default=TypeOfTr.PAYMENT.value, blank=False, null=False)

# 	def save(self, *args, **kwargs):
# 		self.cl_tr_id = Client.objects.tr_count(self.client.id) + 1 #Probably better to use cl_tr_id from last record ?? 
# 		super().save(*args, **kwargs)

# 	def double_visiting(self):
# 		all_visits = self.client.visits.all()
# 		lessons     = [item.lesson for item in all_visits]
# 		return self.lesson in lessons 
		
# 	def clean(self):
# 		tr_number 		 = Client.objects.tr_count(self.client.id)
# 		remained_lessons = self.client.remained_lessons(self)[0]

# 		if (tr_number==0 and self.type_of_tr==TypeOfTr.VISIT.value):
# 			raise ValidationError("You haven't paid to access the lesson")
# 		if (remained_lessons==0 and self.type_of_tr==TypeOfTr.VISIT.value):
# 			raise ValidationError("Your remained lessons number, for this period, is already 0 --> You need to extend the subscription")
# 		if (self.double_visiting()):
# 			raise ValidationError("Double visiting the same lesson on the same time.")

# class Visit(models.Model):
# 	objects = VisitManager()
# 	class Meta:
# 		db_table = 'clients_transactions'
# 		managed = False
# 	cl_tr_id 		= models.PositiveIntegerField(blank=True, null=True, editable=False)		
# 	client			= models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='visits')		
# 	# summ 		 	= models.PositiveSmallIntegerField(default=0,editable=False)
# 	numb_of_lessons = models.PositiveSmallIntegerField(default=1, editable=False)
# 	lesson			= models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE, blank=False)
# 	date_tr 		= models.DateTimeField(auto_now_add=True)
# 	# untill		 	= models.DateField(default=None, editable=False,  blank=True, null=True)
# 	type_of_tr		= models.CharField (max_length=1, choices=TypeOfTr.choices, default=TypeOfTr.VISIT.value, editable=False,blank=False, null=False)

# 	def save(self, *args, **kwargs):
# 		self.cl_tr_id = Client.objects.tr_count(self.client.id) + 1 #Probably better to use cl_tr_id from last record ?? 
# 		super().save(*args, **kwargs)
				
# 	def double_visiting(self):
# 		all_visits = self.client.visits.all()
# 		lessons     = [item.lesson for item in all_visits]
# 		return self.lesson in lessons 		

# 	def clean(self):
# 		tr_number 		 = Client.objects.tr_count(self.client.id)
# 		remained_lessons = self.client.remained_lessons[0]

# 		if (tr_number==0 and self.type_of_tr==TypeOfTr.VISIT.value):
# 			raise ValidationError("You haven't paid to access the lesson")
# 		if (remained_lessons==0 and self.type_of_tr==TypeOfTr.VISIT.value):
# 			raise ValidationError("Your remained lessons number is already 0 --> You need to extend your the subscription")
# 		if (self.double_visiting()):
# 			raise ValidationError("Double visiting the same lesson on the same time.")

# 	def __str__(self):
# 		return f"@Visit: {self.lesson} {self.date_tr.strftime('%d/%m/%y')} by user {self.client}"

# class Payment(models.Model):
# 	objects = PaymentManager()
# 	class Meta:
# 		db_table = 'clients_transactions'
# 		managed = False
# 	cl_tr_id 		= models.PositiveIntegerField(blank=True, null=True, editable=False)	
# 	client			= models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name='payments')
# 	summ 		 	= models.PositiveSmallIntegerField(default=800)	
# 	numb_of_lessons = models.PositiveSmallIntegerField(default=12)
# 	# lesson			= models.ForeignKey('lessons.Lesson', default=None,on_delete=models.CASCADE, editable=False,blank=True, null=True)
# 	date_tr 		= models.DateTimeField(default=timezone.now)
# 	untill		 	= models.DateField(blank=False)
# 	type_of_tr		= models.CharField (max_length=1, choices=TypeOfTr.choices, default=TypeOfTr.PAYMENT.value, editable=False, blank=False, null=False)

# 	def save(self, *args, **kwargs):
# 		self.cl_tr_id = Client.objects.tr_count(self.client.id) + 1 #Probably better to use cl_tr_id from last record ?? 
# 		super().save(*args, **kwargs)
		
# 	def clean(self):
# 		tr_number 		 = Client.objects.tr_count(self.client.id)
# 		remained_lessons = self.client.remained_lessons[0]

# 		if (tr_number==0 and self.type_of_tr==TypeOfTr.VISIT.value):
# 			raise ValidationError("You haven't paid to access the lesson")
# 		if (remained_lessons==0 and self.type_of_tr==TypeOfTr.VISIT.value):
# 			raise ValidationError("Your remained lessons number is already 0 --> You need to extend your the subscription")


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




