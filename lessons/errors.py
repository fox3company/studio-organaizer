from http import HTTPStatus
from django.http import HttpResponse

class HttpResponseNOT_ACCEPTABLE(HttpResponse):
    status_code = HTTPStatus.NOT_ACCEPTABLE