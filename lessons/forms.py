from django import forms
from .models import Lesson
from users.models import Client 



class LessonCreationForm(forms.ModelForm):
	# clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all())
	class Meta:
		model  = Lesson
		fields = ['activity','teacher','quantity','clients','start_date','start_time','end_at','studio']


class LessonChangeForm(forms.ModelForm):
	# clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all())
	class Meta:
		model  = Lesson
		fields = ['activity','teacher','quantity','clients','start_date','start_time','end_at','studio']