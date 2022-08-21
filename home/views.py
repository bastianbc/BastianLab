from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import TemplateView, RedirectView

class Dashboard(TemplateView):
    def get(self, request):
        # <view logic>
        return render(request,'dashboard.html')
