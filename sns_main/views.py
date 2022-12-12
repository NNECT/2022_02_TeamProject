import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
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


class ModifyInfo(View):
    template_name = "modify.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        context = {}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        context = {
            "error_return": {
                "past_password": dict(),
                "password": dict(),
                "re_password": dict(),
                "nickname": dict(),
            },
        }
        chk = True
        post_data = request.POST.copy()
        nickname = post_data["nickname"]
        if nickname == "":
            post_data["nickname"] = request.user.nickname
        else:
            context["error_return"]["nickname"]["value"] = nickname
        form = UserModifyForm(data=post_data, instance=request.user)
        if form.is_valid():
            m = form.save(commit=False)

            past_password = post_data["past_password"]
            context["error_return"]["past_password"]["value"] = past_password
            password = post_data["password"]
            context["error_return"]["password"]["value"] = password
            re_password = post_data["re_password"]
            context["error_return"]["re_password"]["value"] = re_password

            if not request.user.check_password(past_password):
                chk = False
                context["error_return"]["past_password"]["errors"] = True

            if password == "" and re_password == "":
                pass
            elif request.user.check_password(password):
                chk = False
                context["error_return"]["password"]["errors"] = True
            elif password != re_password:
                chk = False
                context["error_return"]["re_password"]["errors"] = True
            else:
                m.password = make_password(password)

            if chk:
                m.save()
                return render(request, self.template_name, context={"success": True})
        return render(request, self.template_name, context=context)


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
                    t = Tag(name=tag)
                    t.save()
                    m.tag.add(t)
                return redirect(request.path)
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
                        t = Tag(name=tag)
                        t.save()
                        m.tag.add(t)
                    return redirect(request.path)
        elif request.POST["form_type"] == "delete_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                m.delete()
                return redirect(request.path)
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
                    t = Tag(name=tag)
                    t.save()
                    m.tag.add(t)
                return redirect(request.path)
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
                        t = Tag(name=tag)
                        t.save()
                        m.tag.add(t)
                    return redirect(request.path)
        elif request.POST["form_type"] == "delete_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                m.delete()
                return redirect(request.path)
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
        pk = kwargs['pk']
        context = {
            "tag_page": True,
            "message_card_list": MessageCard.objects.filter(tag__id=pk),
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
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
                    t = Tag(name=tag)
                    t.save()
                    m.tag.add(t)
                return redirect(request.path)
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
                        t = Tag(name=tag)
                        t.save()
                        m.tag.add(t)
                    return redirect(request.path)
        elif request.POST["form_type"] == "delete_message":
            for _ in [0]:
                try:
                    message_id = int(request.POST["form_id"])
                    m = MessageCard.objects.get(id=message_id)
                except ValueError:
                    break
                m.delete()
                return redirect(request.path)
        context = {
            "tag_page": True,
            "message_card_list": MessageCard.objects.filter(tag__id=pk),
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
                        t = Tag(name=tag)
                        t.save()
                        m.tag.add(t)
                    return redirect(request.path)
            elif request.POST["form_type"] == "delete_message":
                url = card.author.get_absolute_url()
                card.delete()
                return redirect(url)
            elif request.POST["form_type"] == "insert_reply":
                form = ReplyForm(data=request.POST, user=request.user, message=card)
                if form.is_valid():
                    m = form.save(commit=False)
                    m.message = card
                    m.author = request.user
                    m.save()
                    return redirect(request.path)
            elif request.POST["form_type"] == "modify_reply":
                for _ in [0]:
                    try:
                        reply_id = int(request.POST["form_id"])
                        m = Reply.objects.get(id=reply_id)
                    except ValueError:
                        break
                    form = ReplyForm(data=request.POST, user=request.user, message=card, instance=m)
                    if form.is_valid():
                        form.save()
                        return redirect(request.path)
            elif request.POST["form_type"] == "delete_reply":
                for _ in [0]:
                    try:
                        reply_id = int(request.POST["form_id"])
                        m = Reply.objects.get(id=reply_id)
                    except ValueError:
                        break
                    m.delete()
                    return redirect(request.path)
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


@login_required
@require_POST
def user_follow(request):
    chk = request.POST.get('chk', None)
    pk = request.POST.get('pk', None)
    if chk == "author":
        target = get_object_or_404(User, id=pk)
    elif chk == "m":
        card = get_object_or_404(MessageCard, id=pk)
        target = card.author
    elif chk == "r":
        card = get_object_or_404(Reply, id=pk)
        target = card.author
    else:
        return

    if target in request.user.follow.all():
        # 좋아요 취소
        chk = 0
        request.user.follow.remove(target)
    else:
        # 좋아요
        chk = 1
        request.user.follow.add(target)

    context = {
        "followed_chk": chk,
    }
    return HttpResponse(json.dumps(context), content_type="application/json")


@login_required
@require_POST
def card_like(request):
    pk = request.POST.get('pk', None)
    card = get_object_or_404(MessageCard, id=pk)

    if request.user in card.like_user.all():
        # 좋아요 취소
        chk = 0
        card.like_user.remove(request.user)
    else:
        # 좋아요
        chk = 1
        card.like_user.add(request.user)

    context = {
        "liked_chk": chk,
        "like_count": card.like_user.all().count(),
    }
    return HttpResponse(json.dumps(context), content_type="application/json")


@login_required
@require_POST
def card_forward(request):
    pk = request.POST.get('pk', None)
    card = get_object_or_404(MessageCard, id=pk)

    if request.user in card.forward_user.all():
        # 리트윗 취소
        chk = 0
        card.forward_user.remove(request.user)
    else:
        # 리트윗
        chk = 1
        card.forward_user.add(request.user)

    context = {
        "forwarded_chk": chk,
        "forward_count": card.forward_user.all().count(),
    }
    return HttpResponse(json.dumps(context), content_type="application/json")
