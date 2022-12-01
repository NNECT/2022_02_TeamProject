from django.shortcuts import render, redirect
from django.views.generic import View


class Timeline(View):
    template_name = "timeline.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        return render(request, self.template_name)


class Register(View):
    template_name = "register.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('timeline')
        return render(request, self.template_name)