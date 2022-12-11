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
            ).order_by("-created_at"),
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.POST["form_type"] == "insert_message":
            form = TimelineForm(data=request.POST, files=request.FILES, user=request.user)
            if form.is_valid():
                m = form.save(commit=False)
                m.author = request.user
                m.save()
                link_users = m.get_link_users()
                for link_user in link_users:
                    m.link_user.add(link_user)
                tags = m.get_tags()
                addable_tags = m.get_addable_tags()
                for tag in tags:
                    m.tag.add(tag)
                for tag in addable_tags:
                    t = Tag(name=tag, slug=slugify(tag, allow_unicode=True)).save()
                    m.tag.add(t)
                redirect(request.path)
        elif request.POST["form_type"] == "modify_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                form = TimelineForm(data=request.POST, files=request.FILES, user=request.user, instance=m)
                if form.is_valid():
                    m = form.save()
                    m.link_user.clear()
                    link_users = m.get_link_users()
                    for link_user in link_users:
                        m.link_user.add(link_user)
                    m.tag.clear()
                    tags = m.get_tags()
                    addable_tags = m.get_addable_tags()
                    for tag in tags:
                        m.tag.add(tag)
                    for tag in addable_tags:
                        t = Tag(name=tag, slug=slugify(tag, allow_unicode=True)).save()
                        m.tag.add(t)
                    redirect(request.path)
        elif request.POST["form_type"] == "delete_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                m.delete()
                redirect(request.path)
        context = {
            "page_author": request.user,
            "message_card_list": MessageCard.objects.filter(
                Q(author__id=request.user.id) | Q(link_user__id=request.user.id) | Q(forward_user__id=request.user.id)
            ),
        }
        return render(request, self.template_name, context=context)


class TimelineUser(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        try:
            page_author = User.objects.get(username=kwargs['username'])
        except User.DoesNotExist:
            return redirect('timeline')
        context = {
            "page_author": page_author,
            "message_card_list": MessageCard.objects.filter(
                Q(author__id=page_author.id) | Q(link_user__id=page_author.id) | Q(forward_user__id=page_author.id)
            ),
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        try:
            page_author = User.objects.get(username=kwargs['username'])
        except User.DoesNotExist:
            return redirect('timeline')
        if request.POST["form_type"] == "insert_message":
            form = TimelineForm(data=request.POST, files=request.FILES, user=request.user)
            if form.is_valid():
                m = form.save(commit=False)
                m.author = request.user
                m.save()
                link_users = m.get_link_users()
                for link_user in link_users:
                    m.link_user.add(link_user)
                tags = m.get_tags()
                addable_tags = m.get_addable_tags()
                for tag in tags:
                    m.tag.add(tag)
                for tag in addable_tags:
                    t = Tag(name=tag, slug=slugify(tag, allow_unicode=True)).save()
                    m.tag.add(t)
                redirect(request.path)
        elif request.POST["form_type"] == "modify_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                form = TimelineForm(data=request.POST, files=request.FILES, user=request.user, instance=m)
                if form.is_valid():
                    m = form.save()
                    m.link_user.clear()
                    link_users = m.get_link_users()
                    for link_user in link_users:
                        m.link_user.add(link_user)
                    m.tag.clear()
                    tags = m.get_tags()
                    addable_tags = m.get_addable_tags()
                    for tag in tags:
                        m.tag.add(tag)
                    for tag in addable_tags:
                        t = Tag(name=tag, slug=slugify(tag, allow_unicode=True)).save()
                        m.tag.add(t)
                    redirect(request.path)
        elif request.POST["form_type"] == "delete_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                m.delete()
                redirect(request.path)
        context = {
            "page_author": page_author,
            "message_card_list": MessageCard.objects.filter(
                Q(author__id=page_author.id) | Q(link_user__id=page_author.id) | Q(forward_user__id=page_author.id)
            ),
        }
        return render(request, self.template_name, context=context)


class TimelineTag(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        tag_slug = kwargs['tag_slug']
        context = {
            "message_card_list": MessageCard.objects.filter(tag__slug=tag_slug),
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        tag_slug = kwargs['tag_slug']
        if request.POST["form_type"] == "insert_message":
            form = TimelineForm(data=request.POST, files=request.FILES, user=request.user)
            if form.is_valid():
                m = form.save(commit=False)
                m.author = request.user
                m.save()
                link_users = m.get_link_users()
                for link_user in link_users:
                    m.link_user.add(link_user)
                tags = m.get_tags()
                addable_tags = m.get_addable_tags()
                for tag in tags:
                    m.tag.add(tag)
                for tag in addable_tags:
                    t = Tag(name=tag, slug=slugify(tag, allow_unicode=True)).save()
                    m.tag.add(t)
                redirect(request.path)
        elif request.POST["form_type"] == "modify_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                form = TimelineForm(data=request.POST, files=request.FILES, user=request.user, instance=m)
                if form.is_valid():
                    m = form.save()
                    m.link_user.clear()
                    link_users = m.get_link_users()
                    for link_user in link_users:
                        m.link_user.add(link_user)
                    m.tag.clear()
                    tags = m.get_tags()
                    addable_tags = m.get_addable_tags()
                    for tag in tags:
                        m.tag.add(tag)
                    for tag in addable_tags:
                        t = Tag(name=tag, slug=slugify(tag, allow_unicode=True)).save()
                        m.tag.add(t)
                    redirect(request.path)
        elif request.POST["form_type"] == "delete_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                m.delete()
                redirect(request.path)
        context = {
            "message_card_list": MessageCard.objects.filter(tag__slug=tag_slug),
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

    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        for _ in [0]:
            try:
                card = MessageCard.objects.get(id=pk)
            except MessageCard.DoesNotExist:
                break
            if request.POST["form_type"] == "modify_message":
                form = TimelineForm(data=request.POST, files=request.FILES, user=request.user, instance=card)
                if form.is_valid():
                    m = form.save()
                    m.link_user.clear()
                    link_users = m.get_link_users()
                    for link_user in link_users:
                        m.link_user.add(link_user)
                    m.tag.clear()
                    tags = m.get_tags()
                    addable_tags = m.get_addable_tags()
                    for tag in tags:
                        m.tag.add(tag)
                    for tag in addable_tags:
                        t = Tag(name=tag, slug=slugify(tag, allow_unicode=True)).save()
                        m.tag.add(t)
            elif request.POST["form_type"] == "insert_reply":
                form = ReplyForm(data=request.POST, files=request.FILES, user=request.user, message=card)
                if form.is_valid():
                    m = form.save(commit=False)
                    m.message = card
                    m.author = request.user
                    m.save()
            else:
                for _ in [0]:
                    try:
                        reply_id = int(request.POST["form_type"])
                        reply = Reply.objects.get(id=reply_id)
                    except ValueError:
                        break
                    form = ReplyForm(data=request.POST, files=request.FILES, user=request.user, message=card, instance=reply)
                    if form.is_valid():
                        m = form.save()
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
