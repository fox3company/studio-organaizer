# from django.urls import reverse 
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import ListView

from django.utils import timezone
from datetime import timedelta, time, date, datetime

from .models import Lesson, ActivityType, Location, Studio
from users.models import CustomUser, Student, Client
# from activities.models import Visit
# from django.conf import settings


from django.core.exceptions import EmptyResultSet, SuspiciousOperation, PermissionDenied, ObjectDoesNotExist, ValidationError
from django.http import Http404
from .errors import HttpResponseNOT_ACCEPTABLE


now   = timezone.now()
now_time = now.time()
today = timezone.localtime(now).date()

class LessonsListView(ListView):
	template_name 		= "lessons/lessons_list_2.html"
	context_object_name = "lessons"
	queryset 			=  Lesson.objects.all()

	# def get_object(self):
	# 	id_ = self.kwargs.get("id")
	# 	obj = get_object_or_404(Article, id=id_ )
	# 	obj.client_in_lesson = obj.check_client_registration(self.request.User.id)
	# 	return obj 

	def get_queryset(self):
		qset = super().get_queryset()
		year = self.kwargs.get('year')
		week = self.kwargs.get('week')
		# week -= 2 	 
		qset = qset.filter(start_date__year=year).filter(start_date__week=week)
		# day 	 = 3
		for obj in qset:
			obj.client_in_queue 	= obj.check_client_in_queue(self.request.user.id)		
			obj.client_registration = obj.check_client_registration(self.request.user.id)		
			obj.is_today 			= True if today == obj.start_date else False
			obj.missed 	  = True if obj in self.request.user.to_client().missed_lessons() else False
			obj.is_passed = True if (obj.start_date < today) or ((obj.start_date == today) and (obj.end_at < now_time))  else False
			obj.is_future_lesson  = True if obj.is_today is False and obj.is_passed is False else False
			datetime_start =  datetime.combine(obj.start_date, obj.start_time)
			stop_cancelation = (datetime_start - timedelta(hours=8))
			obj.can_unsubscribe   = False if (stop_cancelation.date() < now.date()) or ( (stop_cancelation.date() == now.date()) and (stop_cancelation.time() < now.time()) ) else True
			obj.isoday    = obj.start_date.isoweekday()
			obj.isoweek   = obj.start_date.isocalendar().week
			obj.isoyear   = obj.start_date.isocalendar().year 	
		return qset

		# week = qset[0].start_date.isocalendar().week
		# i = 1 
		# arr = [qset[0]]
		# dictionar = {f"{week}": arr}
		# while i < (len(qset)-1):
		# 	arr.clear()
		# 	while qset[i].start_date.isocalendar().week == week:
		# 		arr.append(qset[i])
		# 		i+=1
		# 	if i == 1:
		# 		pass
		# 	else:
		# 		dictionar[f'{week}'] = arr 
		# 	week+=1
		# return dictionar  

	def _in_range(self, year, week):
		"""
		Returns: [''|None - if has prev week or not,''|None  - if has next week ] ~['',''] | [None,'']
		if It's out of boundaries returns: None 
		"""
		first_lesson = super().get_queryset().first()
		last_lesson = super().get_queryset().last()
		
		a = {'previous_week': '', 'next_week': ''} 
		if first_lesson is not None:
			if year < first_lesson.start_date.isocalendar().year :
				return None
			if first_lesson.start_date.isocalendar().year == year and week < first_lesson.start_date.isocalendar().week:
				return None

			if first_lesson.start_date.isocalendar().year == year:
				if first_lesson.start_date.isocalendar().week == week:
					a['previous_week'] = None				
		else:
			return None

		if last_lesson is not None:
			if year > last_lesson.start_date.isocalendar().year :
				return None
			if last_lesson.start_date.isocalendar().year == year and week > last_lesson.start_date.isocalendar().week:
				return None

			if last_lesson.start_date.isocalendar().year == year:
				if last_lesson.start_date.isocalendar().week == week:
					a['next_week'] = None
		return a 

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		context['missed_lessons'] = self.request.user.to_client().missed_lessons()

		context['now_time'] = now_time
		context['now_date'] = today
		context['now_year'] = sended_year = self.kwargs.get('year')
		context['now_week'] = sended_week = self.kwargs.get('week')	
		context['now_month'] = date.fromisocalendar(sended_year,sended_week,1).month
		context['left_border'] = date.fromisocalendar(sended_year,sended_week,1)	
		context['right_border'] = date.fromisocalendar(sended_year,sended_week,7)

		context['locations'] = Location.objects.all()
		context['remained_lessons'] = self.request.user.to_client().remained_lessons()	
		valid_subs = self.request.user.to_client().payments.all().filter(untill_date__gte=today)
		for obj in valid_subs:
			obj.all_lessons = obj.lessons.all()
			obj.valid = True
		context['subs_now_and_future'] = valid_subs
		context['active_subsc'] = self.request.user.to_client().active_subscription 

		now_week_range_result = self._in_range(sended_year, sended_week)
		
		if now_week_range_result == None:
			pass
		else: 
			if now_week_range_result['previous_week'] == None:
				context['previous_week'] = None
			else: 
				prev_year_week = date.fromisocalendar(sended_year,sended_week,1) - timedelta(weeks=1)
				context['previous_week'] = reverse(	'n_week_lessons', kwargs={'year': prev_year_week.isocalendar().year, 'week': prev_year_week.isocalendar().week})
			
			if now_week_range_result['next_week'] == None:
				context['next_week'] = None
			else: 
				next_year_week = date.fromisocalendar(sended_year,sended_week,1) + timedelta(weeks=1)
				context['next_week'] = reverse(	'n_week_lessons', kwargs={'year': next_year_week.isocalendar().year, 'week': next_year_week.isocalendar().week})
		return context


		# def qs_sort_by_weeks(lesson)
		# 	return lesson.start_date.week 
		# qs = list(self.get_queryset())
		# qs.sort()
		
	def post(self, *args, **kwargs):
		# year 	 = self.kwargs.get('year')
		# week 	 = self.kwargs.get('week')
		line_type = self.request.POST['line_type']
		operation = self.request.POST['operation']
		client_id = self.request.user.id
		client 	  = get_object_or_404(Client,id=client_id)
		lesson_id = self.request.POST['lesson_id']
		lesson    = get_object_or_404(Lesson,id=lesson_id)
		
		year 	 = lesson.start_date.isocalendar().year 	
		week 	 = lesson.start_date.isocalendar().week


		if line_type == 'queue':
			valid_subscr = client.payments.all().filter(from_date__lte=lesson.start_date).filter(untill_date__gte=lesson.start_date).order_by('timestamp')

			if len(valid_subscr) == 0:
					raise HttpResponseNOT_ACCEPTABLE("You don't have a valid subsciption on this period of time")#ObjectDoesNotExist()

			if len(valid_subscr) >= 1:
				valid_subscr=valid_subscr[0]
				if operation == '+':
					lesson.queue.add(client)
					return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))
				if operation == '-':
					lesson.queue.remove(client)
					return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))

		else: 
			# if client.active_subscription and client.active_subscription.from_date <= lesson.start_date and lesson.start_date <= client.active_subscription.untill_date:
			# 	if operation == '+':
			# 		if client.active_subscription.subs_is_valid_for_today():
			# 			client.active_subscription.remains_lessons -= 1
			# 			client.active_subscription.lessons.add(lesson)
			# 			client.active_subscription.save()
			# 			lesson.clients.add(client)
			# 			return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))
			# 		else:			
			# 			raise HttpResponseNOT_ACCEPTABLE("On this period, you've already spent your lessons")
			# 	if operation == '-':
			# 		client.active_subscription.remains_lessons += 1
			# 		client.active_subscription.lessons.remove(lesson)
			# 		client.active_subscription.save()
			# 		lesson.clients.remove(client)
			# 		return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))		
			# else: 
			valid_subscr = client.payments.all().filter(from_date__lte=lesson.start_date).filter(untill_date__gte=lesson.start_date).order_by('timestamp')
			
			if len(valid_subscr) == 0:
				raise HttpResponseNOT_ACCEPTABLE("You don't have a valid subsciption on this period of time")#ObjectDoesNotExist()

			if len(valid_subscr) >= 1:
				valid_subscr=valid_subscr[0]
				if operation == '+':
					if valid_subscr.remains_lessons > 0:
						valid_subscr.remains_lessons -= 1
						valid_subscr.lessons.add(lesson)
						valid_subscr.save()
						lesson.clients.add(client)
						return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))
					else:			
						raise HttpResponseNOT_ACCEPTABLE("On this period, you've already spent your lessons")#
				if operation == '-':
					if lesson.clients.count() == lesson.quantity:
						q_clnts = lesson.queue.all()
						if len(q_clnts) > 0:
							q_cl = q_clnts[0]
							i = 0
							while i < len(q_clnts): 
								valid_subs_q_cl = q_cl.payments.all().filter(from_date__lte=lesson.start_date).filter(untill_date__gte=lesson.start_date).order_by('timestamp')
								if len(valid_subs_q_cl) == 0:
									i += 1
									continue
								else: 
									valid_subs_q_cl = valid_subs_q_cl[0]
									if valid_subs_q_cl.remains_lessons == 0:
										i += 1
										continue
									else:
										valid_subs_q_cl.remains_lessons -= 1
										valid_subs_q_cl.lessons.add(lesson)
										valid_subs_q_cl.save()
										lesson.clients.add(q_cl)
										lesson.queue.remove(q_cl)
										break

					valid_subscr.remains_lessons += 1
					valid_subscr.lessons.remove(lesson)
					valid_subscr.save()
					lesson.clients.remove(client)
					return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))

		return HttpResponseNOT_ACCEPTABLE("You don't have any valid subsciption") #ObjectDoesNotExist()

class LocationLessonsListView(ListView):
	template_name 		= "lessons/lessons_list_2.html"
	context_object_name = "lessons"
	queryset 			=  Lesson.objects.all()

	def get_queryset(self):
		qset 	 = super().get_queryset()
		year  	 = self.kwargs.get('year')
		week 	 = self.kwargs.get('week')
		location = self.kwargs.get('location')
		qset = qset.filter(studio__geo_location__url_name__exact=location).filter(start_date__year=year).filter(start_date__week=week)
		for obj in qset:
			obj.client_in_queue 	= obj.check_client_in_queue(self.request.user.id)		
			obj.client_registration = obj.check_client_registration(self.request.user.id)		
			obj.is_today 			= True if today == obj.start_date else False
			obj.missed 	  = True if obj in self.request.user.to_client().missed_lessons() else False
			obj.is_passed = True if (obj.start_date < today) or ((obj.start_date == today) and (obj.end_at < now_time))  else False
			obj.is_future_lesson  = True if obj.is_today is False and obj.is_passed is False else False
			stop_cancelation = (now - timedelta(hours=8))
			obj.can_unsubscribe   = False if (stop_cancelation.date() < now.date()) or ( (stop_cancelation.date() == now.date()) and (stop_cancelation.time() < now.time()) ) else True
			obj.isoday    = obj.start_date.isoweekday()
			obj.isoweek   = obj.start_date.isocalendar().week
			obj.isoyear   = obj.start_date.isocalendar().year 	
		return qset

	def _in_range(self, year, week):
		"""
		Returns: [''|None - if has prev week or not,''|None  - if has next week ] ~['',''] | [None,'']
		if It's out of boundaries returns: None 
		"""
		first_lesson = super().get_queryset().first()
		last_lesson = super().get_queryset().last()
		a = {'previous_week': '', 'next_week': ''} 
		if first_lesson is not None:
			if year < first_lesson.start_date.isocalendar().year :
				return None
			if first_lesson.start_date.isocalendar().year == year and week < first_lesson.start_date.isocalendar().week:
				return None

			if first_lesson.start_date.isocalendar().year == year:
				if first_lesson.start_date.isocalendar().week == week:
					a['previous_week'] = None				
		else:
			return None

		if last_lesson is not None:
			if year > last_lesson.start_date.isocalendar().year :
				return None
			if last_lesson.start_date.isocalendar().year == year and week > last_lesson.start_date.isocalendar().week:
				return None

			if last_lesson.start_date.isocalendar().year == year:
				if last_lesson.start_date.isocalendar().week == week:
					a['next_week'] = None
		return a 

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		context['missed_lessons'] = self.request.user.to_client().missed_lessons()

		context['now_time'] = now_time
		context['now_date'] = today
		context['now_year'] = sended_year = self.kwargs.get('year')
		context['now_week'] = sended_week = self.kwargs.get('week')	
		context['now_location'] = self.kwargs.get('location')
		context['now_month'] = date.fromisocalendar(sended_year,sended_week,1).month
		context['left_border'] = date.fromisocalendar(sended_year,sended_week,1)	
		context['right_border'] = date.fromisocalendar(sended_year,sended_week,7)

		context['locations'] = Location.objects.all()
		context['remained_lessons'] = self.request.user.to_client().remained_lessons()	
		valid_subs = self.request.user.to_client().payments.all().filter(untill_date__gte=today)
		for obj in valid_subs:
			obj.all_lessons = obj.lessons.all()
			obj.valid = True
		context['subs_now_and_future'] = valid_subs
		context['active_subsc'] = self.request.user.to_client().active_subscription 
		
		now_week_range_result = self._in_range(sended_year, sended_week)
		
		if now_week_range_result == None:
			pass
		else: 
			if now_week_range_result['previous_week'] == None:
				context['previous_week'] = None
			else: 
				prev_year_week = date.fromisocalendar(sended_year,sended_week,1) - timedelta(weeks=1)
				context['previous_week'] = reverse(	'n_week_lessons', kwargs={'year': prev_year_week.isocalendar().year, 'week': prev_year_week.isocalendar().week})
			
			if now_week_range_result['next_week'] == None:
				context['next_week'] = None
			else: 
				next_year_week = date.fromisocalendar(sended_year,sended_week,1) + timedelta(weeks=1)
				context['next_week'] = reverse(	'n_week_lessons', kwargs={'year': next_year_week.isocalendar().year, 'week': next_year_week.isocalendar().week})
		return context


		# def qs_sort_by_weeks(lesson)
		# 	return lesson.start_date.week 
		# qs = list(self.get_queryset())
		# qs.sort()
		
	def post(self, *args, **kwargs):
		# year 	 = self.kwargs.get('year')
		# week 	 = self.kwargs.get('week')
		line_type = self.request.POST['line_type']
		operation = self.request.POST['operation']
		client_id = self.request.user.id
		client 	  = get_object_or_404(Client,id=client_id)
		lesson_id = self.request.POST['lesson_id']
		lesson    = get_object_or_404(Lesson,id=lesson_id)
		
		year 	 = lesson.start_date.isocalendar().year 	
		week 	 = lesson.start_date.isocalendar().week


		if line_type == 'queue':
			valid_subscr = client.payments.all().filter(from_date__lte=lesson.start_date).filter(untill_date__gte=lesson.start_date).order_by('timestamp')

			if len(valid_subscr) == 0:
					raise HttpResponseNOT_ACCEPTABLE("You don't have a valid subsciption on this period of time")#ObjectDoesNotExist()

			if len(valid_subscr) >= 1:
				valid_subscr=valid_subscr[0]
				if operation == '+':
					lesson.queue.add(client)
					return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))
				if operation == '-':
					lesson.queue.remove(client)
					return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))

		else: 
			valid_subscr = client.payments.all().filter(from_date__lte=lesson.start_date).filter(untill_date__gte=lesson.start_date).order_by('timestamp')
			
			if len(valid_subscr) == 0:
				raise HttpResponseNOT_ACCEPTABLE("You don't have a valid subsciption on this period of time")#ObjectDoesNotExist()

			if len(valid_subscr) >= 1:
				valid_subscr=valid_subscr[0]
				if operation == '+':
					if valid_subscr.remains_lessons > 0:
						valid_subscr.remains_lessons -= 1
						valid_subscr.lessons.add(lesson)
						valid_subscr.save()
						lesson.clients.add(client)
						return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))
					else:			
						raise HttpResponseNOT_ACCEPTABLE("On this period, you've already spent your lessons")#
				if operation == '-':
					if lesson.clients.count() == lesson.quantity:
						q_clnts = lesson.queue.all()
						if len(q_clnts) > 0:
							q_cl = q_clnts[0]
							i = 0
							while i < len(q_clnts): 
								valid_subs_q_cl = q_cl.payments.all().filter(from_date__lte=lesson.start_date).filter(untill_date__gte=lesson.start_date).order_by('timestamp')
								if len(valid_subs_q_cl) == 0:
									i += 1
									continue
								else: 
									valid_subs_q_cl = valid_subs_q_cl[0]
									if valid_subs_q_cl.remains_lessons == 0:
										i += 1
										continue
									else:
										valid_subs_q_cl.remains_lessons -= 1
										valid_subs_q_cl.lessons.add(lesson)
										valid_subs_q_cl.save()
										lesson.clients.add(q_cl)
										lesson.queue.remove(q_cl)
										break

					valid_subscr.remains_lessons += 1
					valid_subscr.lessons.remove(lesson)
					valid_subscr.save()
					lesson.clients.remove(client)
					return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))

		return HttpResponseNOT_ACCEPTABLE("You don't have any valid subsciption") #ObjectDoesNotExist()

class ActivityTypesListView(ListView):
	template_name 		= "lessons/activity_types_list.html"
	context_object_name = "types_of_activities"
	queryset 			=  ActivityType.objects.all()

	# def get_object(self):
	# 	id_ = self.kwargs.get("id")
	# 	obj = get_object_or_404(Article, id=id_ )
	# 	return obj 

	def get_queryset(self):
		qset = super().get_queryset()
		return qset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

class LocationsStudiosListView(ListView):
	template_name 		= "lessons/studios.html"
	context_object_name = "locations"
	queryset 			=  Location.objects.all()

	# def get_object(self):
	# 	id_ = self.kwargs.get("id")
	# 	obj = get_object_or_404(Article, id=id_ )
	# 	return obj 

	def get_queryset(self):
		qset = super().get_queryset()
		for obj in qset:
			obj.all_studios = obj.studios.all()
		return qset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return context

		
	