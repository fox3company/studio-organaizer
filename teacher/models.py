from django.db import models
from django.core.validators import RegexValidator
# Create your models here.


class Team(models.Model):
	team_name = models.CharField(max_length=25, unique=True)

	def __str__(self):
		return self.team_name

class Teacher(models.Model):
	name 	 	 = models.CharField(max_length=35)
	about	 	 = models.TextField()
	avatar   	 = models.ImageField(upload_to='teachers/', height_field=None, width_field=None)
	phone_regex  = RegexValidator(regex=r'^0?\d{9,15}$', message="Phone number must be entered in the local format: '0XXXXXXXX'.")
	phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
	org_team 	 = models.ForeignKey('Team',on_delete=models.CASCADE)

	def __str__(self):
		return self.name


