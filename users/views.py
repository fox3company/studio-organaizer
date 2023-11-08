from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from .forms import CustomUserLoginForm
# from .model import StudentCreationForm
from django.views.generic import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from .models import Teacher, Client
from lessons.models import Lesson
from activities.models import Payment

from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta, time, date, datetime
from calendar import monthrange

now   = timezone.now()
now_time = now.time()
today = timezone.localtime(now).date()


class StudentLoginView(auth_views.LoginView):
	next_page = 'now_week_lessons'
 # 	  form_class = StudenLoginForm
	authentication_form = CustomUserLoginForm
 #    next_page = None
 #    redirect_field_name = REDIRECT_FIELD_NAME
	redirect_authenticated_user = True
	template_name = "users/registration/login_student.html"
 #    redirect_authenticated_user = False
 #    extra_context = None


class StudentLogoutView(auth_views.LogoutView):
	  next_page = settings.LOGOUT_REDIRECT_URL
 # 	  form_class = StudenLoginForm
 #    redirect_field_name = REDIRECT_FIELD_NAME
	# template_name = "users/registration/login_student.html"
 #    redirect_authenticated_user = False
 #    extra_context = None

# class StudentCreationView(CreateView):
# 	template_name = "student/registration/registration_student.html"
# 	form_class    = StudentCreationForm


class TeachersListView(ListView):
    template_name       = "users/teachers_list.html"
    context_object_name = "teachers"
    queryset            =  Teacher.objects.all()

    # def get_object(self):
    #   id_ = self.kwargs.get("id")
    #   obj = get_object_or_404(Article, id=id_ )
    #   return obj 

    def get_queryset(self):
        qset = super().get_queryset()
        return qset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PaymentsListView(ListView):
    template_name       = "users/payments.html"
    context_object_name = "payments"
    queryset            =  Payment.objects.all()

    # def get_object(self):
    #   id_ = self.kwargs.get("id")
    #   obj = get_object_or_404(Article, id=id_ )
    #   return obj 

    def get_queryset(self):
        qset = super().get_queryset()
        year  = self.kwargs.get('year')
        qset = qset.filter(client__exact=self.request.user.to_client()).order_by('timestamp').filter(from_date__year=year)
        valid_subscr = self.request.user.to_client().payments.all().filter(untill_date__gte=today)
        for obj in qset:
            if obj in valid_subscr:
                obj.valid = True
            else:
                obj.valid = False 
            obj.all_lessons = obj.lessons.all()
        return qset

    def _in_range(self, year):
        """
        Returns: [''|None - if has prev year or not,''|None  - if has next year or not ] ~ ['',''] | [None,'']
        if It's out of boundaries returns: None 
        """
        first_subs = super().get_queryset().filter(client__exact=self.request.user.to_client()).order_by('timestamp').first()
        last_subs  = super().get_queryset().filter(client__exact=self.request.user.to_client()).order_by('timestamp').last()

        a = {'previous_year': '', 'next_year': ''} 
        
        if first_subs is not None:
            if year < first_subs.from_date.year :
                return None

            if first_subs.from_date.year == year:
                a['previous_year'] = None               
        else:
            raise EmptyResultSet()

        if last_subs is not None:
            if year > last_subs.from_date.year:
                return None

            if last_subs.from_date.year == year:
                a['next_year'] = None

        print(f"##########Year: {year}")
        print(f"##########Result: {a}")
        return a 

    def get_context_data(self, **kwargs):
        page_year  = self.kwargs.get('year')

        context = super().get_context_data(**kwargs)

        context['active_subsc'] = self.request.user.to_client().active_subscription 

        now_year_range_result = self._in_range(page_year)
        
        if now_year_range_result == None:
            raise SuspiciousOperation()
        if now_year_range_result['previous_year'] == None:
            context['previous_year'] = None
        else: 
            prev_page_year  = page_year - 1
            context['previous_year'] = reverse( 'payments_n_year', kwargs={'year': prev_page_year})
        
        if now_year_range_result['next_year'] == None:
            context['next_year'] = None
        else: 
            next_page_year  = page_year + 1
            context['next_year'] = reverse( 'payments_n_year', kwargs={'year': next_page_year})

        return context



class ProfileView(ListView):
    template_name       = "users/profile.html"
    context_object_name = "lessons"
    # queryset            =  Lesson.objects.all()

    def get_queryset(self):
        plus_3_weeks       = today + timedelta(weeks=3)  
        quering_end_date   = date.fromisocalendar(plus_3_weeks.isocalendar().year,plus_3_weeks.isocalendar().week,7)    
        qset  = self.request.user.to_client().lessons.all().filter(start_date__gte=today).exclude(start_date__gt=quering_end_date)
        # second_part = Lesson.objects.all().filter(start_date__gte=today).filter(queue__exact=self.request.user.to_client())
        # for obj in second_part:
        #     obj.client_registration = False
        #     obj.client_in_queue     = True
        # Lesson.objects.none()
        # qset.union(first_part,second_part)    

        for obj in qset:
            obj.client_registration = True
            obj.client_in_queue     = False

            obj.isoday    = obj.start_date.isoweekday()
            obj.isoweek   = obj.start_date.isocalendar().week
            obj.isoyear   = obj.start_date.isocalendar().year   

            obj.is_today  = True if today == obj.start_date else False
            obj.missed    = True if obj in self.request.user.to_client().missed_lessons() else False
            obj.is_passed = True if (obj.start_date < today) or ((obj.start_date == today) and (obj.end_at < now_time))  else False
            obj.is_future_lesson  = True if obj.is_today is False and obj.is_passed is False else False
            
            stop_cancelation_time = (now - timedelta(hours=8)).time()
            obj.can_unsubscribe   = True if ((obj.start_date < today) or ((obj.start_date < today) and (now_time < stop_cancelation_time))) and obj.is_passed is not True  else False
        return qset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queue_lessons = Lesson.objects.all().filter(start_date__gte=today).filter(queue__exact=self.request.user.to_client())
        for obj in queue_lessons:
            obj.client_registration = False
            obj.client_in_queue     = True
            # obj.isoday    = obj.start_date.isoweekday()
            # obj.isoweek   = obj.start_date.isocalendar().week
            # obj.isoyear   = obj.start_date.isocalendar().year   
            obj.is_today  = True if today == obj.start_date else False
            obj.missed    = True if obj in self.request.user.to_client().missed_lessons() else False
            obj.is_passed = True if (obj.start_date < today) or ((obj.start_date == today) and (obj.end_at < now_time))  else False
            obj.is_future_lesson  = True if obj.is_today is False and obj.is_passed is False else False
            
            stop_cancelation_time = (now - timedelta(hours=8)).time()
            obj.can_unsubscribe   = True if ((obj.start_date < today) or ((obj.start_date < today) and (now_time < stop_cancelation_time))) and obj.is_passed is not True  else False
        
        context['queue_lessons'] =  queue_lessons
        # context['missed_lessons'] = self.request.user.to_client().missed_lessons()
        context['client'] = self.request.user.to_client()
        context['active_subsc'] = self.request.user.to_client().active_subscription 
        context['with_us'] = self.request.user.to_client().with_us()

        context['now_time'] = now_time
        context['now_date'] = today
        # context['now_year'] = sended_year = self.kwargs.get('year')
        # context['now_week'] = sended_week = self.kwargs.get('week') 
        # context['now_month'] = today.month
        # context['left_border'] = date.fromisocalendar(sended_year,sended_week,1)    
        # context['right_border'] = date.fromisocalendar(sended_year,sended_week,7)

        # context['remained_lessons'] = self.request.user.to_client().remained_lessons()  
        valid_subs = self.request.user.to_client().payments.all().filter(untill_date__gte=today)
        for obj in valid_subs:
            obj.all_lessons = obj.lessons.all()
            obj.valid = True
        context['subs_now_and_future'] = valid_subs
    
        return context


        # def qs_sort_by_weeks(lesson)
        #   return lesson.start_date.week 
        # qs = list(self.get_queryset())
        # qs.sort()
        
    def post(self, *args, **kwargs):
        # year   = self.kwargs.get('year')
        # week   = self.kwargs.get('week')
        line_type = self.request.POST['line_type']
        operation = self.request.POST['operation']
        client_id = self.request.user.id
        client    = get_object_or_404(Client,id=client_id)
        lesson_id = self.request.POST['lesson_id']
        lesson    = get_object_or_404(Lesson,id=lesson_id)
        
        year     = lesson.start_date.isocalendar().year     
        week     = lesson.start_date.isocalendar().week


        if line_type == 'queue':
            valid_subscr = client.payments.all().filter(from_date__lte=lesson.start_date).filter(untill_date__gte=lesson.start_date).order_by('timestamp')

            if len(valid_subscr) == 0:
                    raise HttpResponseNOT_ACCEPTABLE("You don't have a valid subsciption on this period of time")#ObjectDoesNotExist()

            if len(valid_subscr) >= 1:
                valid_subscr=valid_subscr[0]
                if operation == '+':
                    lesson.queue.add(client)
                    return redirect(reverse("profile"))
                if operation == '-':
                    lesson.queue.remove(client)
                    return redirect(reverse("profile"))

        else: 
            # if client.active_subscription and client.active_subscription.from_date <= lesson.start_date and lesson.start_date <= client.active_subscription.untill_date:
            #   if operation == '+':
            #       if client.active_subscription.subs_is_valid_for_today():
            #           client.active_subscription.remains_lessons -= 1
            #           client.active_subscription.lessons.add(lesson)
            #           client.active_subscription.save()
            #           lesson.clients.add(client)
            #           return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))
            #       else:           
            #           raise HttpResponseNOT_ACCEPTABLE("On this period, you've already spent your lessons")
            #   if operation == '-':
            #       client.active_subscription.remains_lessons += 1
            #       client.active_subscription.lessons.remove(lesson)
            #       client.active_subscription.save()
            #       lesson.clients.remove(client)
            #       return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))       
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
                        return redirect(reverse("profile"))
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
                    return redirect(reverse("profile"))

        return HttpResponseNOT_ACCEPTABLE("You don't have any valid subsciption") #ObjectDoesNotExist()

class RegistrationsView(ListView):
    template_name       = "users/registrations.html"
    context_object_name = "lessons"
    # queryset            =  Lesson.objects.all()

# def get_object(self):
    #   id_ = self.kwargs.get("id")
    #   obj = get_object_or_404(Article, id=id_ )
    #   obj.client_in_lesson = obj.check_client_registration(self.request.User.id)
    #   return obj 

    def get_queryset(self):
        year  = self.kwargs.get('year')
        month = self.kwargs.get('month')
         
        first_part  = self.request.user.to_client().lessons.all().filter(start_date__year=year).filter(start_date__month=month)
        # for obj in first_part:
        #     obj.client_registration = True
        #     obj.client_in_queue     = False
        
        second_part = Lesson.objects.all().filter(start_date__gte=today).filter(queue__exact=self.request.user.to_client()).filter(start_date__month=month)
        # for obj in second_part:
        #     obj.client_registration = False
        #     obj.client_in_queue     = True

        qset = first_part|second_part
        # print(f"############Qset: {qset.all().values()}")
        # print(f"############First part: {first_part.all().values()}")
        # print(f"############Second part: {second_part.all().values()}")
        for obj in qset:
            obj.client_in_queue     = obj.check_client_in_queue(self.request.user.id)       
            obj.client_registration = obj.check_client_registration(self.request.user.id)       

            obj.isoday    = obj.start_date.isoweekday()
            obj.isoweek   = obj.start_date.isocalendar().week
            obj.isoyear   = obj.start_date.isocalendar().year   

            obj.is_today  = True if today == obj.start_date else False
            obj.missed    = True if obj in self.request.user.to_client().missed_lessons() else False
            obj.is_passed = True if (obj.start_date < today) or ((obj.start_date == today) and (obj.end_at < now_time))  else False
            obj.is_future_lesson  = True if obj.is_today is False and obj.is_passed is False else False
            
            stop_cancelation_time = (now - timedelta(hours=8)).time()
            obj.can_unsubscribe   = True if ((obj.start_date < today) or ((obj.start_date < today) and (now_time < stop_cancelation_time))) and obj.is_passed is not True  else False
        return qset

    def _in_range(self, year, month):
        """
        Returns: [''|None - if has prev month or not,''|None  - if has next month ] ~['',''] | [None,'']
        if It's out of boundaries returns: None 
        """
        first_lesson = self.request.user.to_client().lessons.all().order_by('start_date').first()
        last_lesson = self.request.user.to_client().lessons.all().order_by('start_date').last()
        query_last_lesson = Lesson.objects.all().filter(queue__exact=self.request.user.to_client()).last()

        if last_lesson and query_last_lesson and last_lesson.start_date < query_last_lesson.start_date:
            last_lesson = query_last_lesson

        a = {'previous_month': '', 'next_month': ''} 
        
        if first_lesson is not None:
            if year < first_lesson.start_date.year :
                return None
            if first_lesson.start_date.year == year and month < first_lesson.start_date.month:
                return None

            if first_lesson.start_date.year == year:
                if first_lesson.start_date.month == month:
                    a['previous_month'] = None               
        else:
            return None

        if last_lesson is not None:
            if year > last_lesson.start_date.year :
                return None
            if last_lesson.start_date.year == year and month > last_lesson.start_date.month:
                return None

            if last_lesson.start_date.year == year:
                if last_lesson.start_date.month == month:
                    a['next_month'] = None
        return a 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['missed_lessons'] = self.request.user.to_client().missed_lessons()
        context['now_time'] = now_time
        context['now_date'] = today
        context['page_year'] = page_year = self.kwargs.get('year')
        context['page_month'] = page_month = self.kwargs.get('month') 

        context['left_border'] = date(page_year,page_month,1)    
        context['right_border'] = date(page_year,page_month,monthrange(page_year,page_month)[1])

        now_month_range_result = self._in_range(page_year, page_month)
        
        if now_month_range_result == None:
            pass 
        else:
            if now_month_range_result['previous_month'] == None:
                context['previous_month'] = None
            else: 
                prev_page_month = page_month
                prev_page_year  = page_year

                if page_month == 1:
                    prev_page_year -= 1
                    prev_page_month = 12
                else:
                    prev_page_month -= 1

                context['previous_month'] = reverse( 'registrations_year_month', kwargs={'year': prev_page_year, 'month': prev_page_month})
            
            if now_month_range_result['next_month'] == None:
                context['next_month'] = None
            else: 
                next_page_month = page_month
                next_page_year  = page_year

                if page_month == 12:
                    next_page_year += 1
                    next_page_month = 1
                else:
                    next_page_month += 1

                context['next_month'] = reverse( 'registrations_year_month', kwargs={'year': next_page_year, 'month': next_page_month})
    
        return context


        # def qs_sort_by_weeks(lesson)
        #   return lesson.start_date.week 
        # qs = list(self.get_queryset())
        # qs.sort()
        
    def post(self, *args, **kwargs):
        # year   = self.kwargs.get('year')
        # week   = self.kwargs.get('week')
        line_type = self.request.POST['line_type']
        operation = self.request.POST['operation']
        client_id = self.request.user.id
        client    = get_object_or_404(Client,id=client_id)
        lesson_id = self.request.POST['lesson_id']
        lesson    = get_object_or_404(Lesson,id=lesson_id)
        
        year     = lesson.start_date.isocalendar().year     
        week     = lesson.start_date.isocalendar().week


        if line_type == 'queue':
            valid_subscr = client.payments.all().filter(from_date__lte=lesson.start_date).filter(untill_date__gte=lesson.start_date).order_by('timestamp')

            if len(valid_subscr) == 0:
                    raise HttpResponseNOT_ACCEPTABLE("You don't have a valid subsciption on this period of time")#ObjectDoesNotExist()

            if len(valid_subscr) >= 1:
                valid_subscr=valid_subscr[0]
                if operation == '+':
                    lesson.queue.add(client)
                    return redirect(reverse("profile"))
                if operation == '-':
                    lesson.queue.remove(client)
                    return redirect(reverse("profile"))

        else: 
            # if client.active_subscription and client.active_subscription.from_date <= lesson.start_date and lesson.start_date <= client.active_subscription.untill_date:
            #   if operation == '+':
            #       if client.active_subscription.subs_is_valid_for_today():
            #           client.active_subscription.remains_lessons -= 1
            #           client.active_subscription.lessons.add(lesson)
            #           client.active_subscription.save()
            #           lesson.clients.add(client)
            #           return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))
            #       else:           
            #           raise HttpResponseNOT_ACCEPTABLE("On this period, you've already spent your lessons")
            #   if operation == '-':
            #       client.active_subscription.remains_lessons += 1
            #       client.active_subscription.lessons.remove(lesson)
            #       client.active_subscription.save()
            #       lesson.clients.remove(client)
            #       return redirect(reverse("n_week_lessons",kwargs = {"year": year, "week": week }))       
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
                        return redirect(reverse("profile"))
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
                    return redirect(reverse("profile"))

        return HttpResponseNOT_ACCEPTABLE("You don't have any valid subsciption") #ObjectDoesNotExist()

