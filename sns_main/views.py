from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import View, FormView
from django.contrib.auth import authenticate, login
from .forms import *
from .models import *


class Login(FormView):
    template_name = "login.html"
    form_class = LoginForm
    success_url = '/'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('timeline')
        return render(request, self.template_name)

    def form_valid(self, form):
        user = authenticate(
            self.request,
            username=form.cleaned_data.get("username"),
            password=form.cleaned_data.get("password")
        )
        if user is not None:
            login(self.request, user=user)
        return super().form_valid(form)


class Register(FormView):
    template_name = "register.html"
    form_class = RegisterForm
    success_url = "/"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('timeline')
        return render(request, self.template_name)

    def form_valid(self, form):
        user = authenticate(
            self.request,
            username=form.cleaned_data.get("username"),
            password=form.cleaned_data.get("password")
        )
        if user is not None:
            login(self.request, user=user)
        return super().form_valid(form)


class Timeline(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        context = {
            "page_author": request.user,
            "message_card_list": MessageCard.objects.filter(
                Q(author__id=request.user.id) | Q(link_user__id=request.user.id) | Q(forward_user__id=request.user.id)
            ).order_by("created_at"),
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        context = {
            "page_author": request.user,
            "message_card_list": MessageCard.objects.filter(
                Q(author__id=request.user.id) | Q(link_user__id=request.user.id) | Q(forward_user__id=request.user.id)
            ).order_by("created_at"),
        }
        return render(request, self.template_name, context=context)


class TimelineUser(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=kwargs['username'])
        context = {
            "page_author": user,
            "message_card_list": MessageCard.objects.filter(
                Q(author__id=user.id) | Q(link_user__id=user.id) | Q(forward_user__id=user.id)
            ).order_by("created_at"),
        }
        return render(request, self.template_name, context=context)


class TimelineTag(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        tag_slug = kwargs['tag_slug']
        context = {
            "page_author": "",
            "message_card_list": MessageCard.objects.filter(tag__slug=tag_slug).order_by("created_at"),
        }
        return render(request, self.template_name, context=context)


class TimelineDetail(View):
    template_name = "detail.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        context = {
            "message_card": MessageCard.objects.get(id=pk),
            "reply_list": Reply.objects.filter(message__id=pk),
        }
        return render(request, self.template_name, context=context)


class UserFollowList(View):
    template_name = "follow.html"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=kwargs['username'])
        context = {
            "page_author": user,
            "follow_user_list": User.objects.get(id=user.id).follow.all(),
        }
        return render(request, self.template_name, context=context)


class UserFollowerList(View):
    template_name = "follower.html"

    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=kwargs['username'])
        context = {
            "page_author": user,
            "follower_user_list": User.objects.filter(follow__id=user.id),
        }
        return render(request, self.template_name, context=context)
