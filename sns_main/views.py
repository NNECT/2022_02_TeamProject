from django.db.models import Q, Count
from django.shortcuts import render, redirect
from django.views.generic import View
from .models import *


class Timeline(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        context = {
            "message_card_list": MessageCard.objects.filter(Q(author__id=request.user.id) | Q(link_user__id=request.user.id) | Q(forward_user__id=request.user.id)).order_by("created_at"),
        }
        return render(request, self.template_name, context=context)


class TimelineUser(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        username = kwargs['username']
        context = {
            "message_card_list": MessageCard.objects.filter(Q(author__username=username) | Q(link_user__username=username) | Q(forward_user__username=username)).order_by("created_at"),
        }
        return render(request, self.template_name, context=context)


class TimelineDetail(View):
    template_name = "detail.html"

    def get(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return redirect('login')
        pk = kwargs['pk']
        context = {
            "message_card": MessageCard.objects.get(id=pk),
            "reply_list": Reply.objects.filter(message__id=pk),
        }
        return render(request, self.template_name, context=context)


class Register(View):
    template_name = "register.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('timeline')
        return render(request, self.template_name)