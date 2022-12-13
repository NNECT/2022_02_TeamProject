import json
import math
import operator
from functools import reduce

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import View, FormView

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
        data_list = MessageCard.objects.filter(
            Q(author__id=request.user.id) | Q(link_user__id=request.user.id) | Q(forward_user__id=request.user.id)
        )
        size = data_list.count()
        if size > 10:
            data_list = data_list[:10]
        context = {
            "page_author": request.user,
            "pages": math.ceil(size / 10),
            "message_card_list": data_list,
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

        data_list = MessageCard.objects.filter(
            Q(author__id=request.user.id) | Q(link_user__id=request.user.id) | Q(forward_user__id=request.user.id)
        )
        size = data_list.count()
        if size > 10:
            data_list = data_list[:10]
        context = {
            "page_author": request.user,
            "pages": math.ceil(size / 10),
            "message_card_list": data_list,
        }
        return render(request, self.template_name, context=context)


class TimelineFeed(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        data_list = MessageCard.objects.filter(
            Q(author__id=request.user.id) | Q(link_user__id=request.user.id) | Q(forward_user__id=request.user.id) |
            Q(author__in=request.user.follow.all()) | Q(forward_user__in=request.user.follow.all())
        )
        size = data_list.count()
        if size > 10:
            data_list = data_list[:10]
        context = {
            "feed": True,
            "page_author": request.user,
            "pages": math.ceil(size / 10),
            "message_card_list": data_list,
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

        data_list = MessageCard.objects.filter(
            Q(author__id=request.user.id) | Q(link_user__id=request.user.id) | Q(forward_user__id=request.user.id) |
            Q(author__in=request.user.follow.all()) | Q(forward_user__in=request.user.follow.all())
        )
        size = data_list.count()
        if size > 10:
            data_list = data_list[:10]
        context = {
            "feed": True,
            "page_author": request.user,
            "pages": math.ceil(size / 10),
            "message_card_list": data_list,
        }
        return render(request, self.template_name, context=context)


class TimelineUser(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        try:
            page_author = User.objects.get(username=kwargs['username'])
        except User.DoesNotExist:
            return redirect('timeline')

        data_list = MessageCard.objects.filter(
            Q(author__id=page_author.id) | Q(link_user__id=page_author.id) | Q(forward_user__id=page_author.id)
        )
        size = data_list.count()
        if size > 10:
            data_list = data_list[:10]
        context = {
            "page_author": page_author,
            "pages": math.ceil(size / 10),
            "message_card_list": data_list,
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

        data_list = MessageCard.objects.filter(
            Q(author__id=page_author.id) | Q(link_user__id=page_author.id) | Q(forward_user__id=page_author.id)
        )
        size = data_list.count()
        if size > 10:
            data_list = data_list[:10]
        context = {
            "page_author": page_author,
            "pages": math.ceil(size / 10),
            "message_card_list": data_list,
        }
        return render(request, self.template_name, context=context)


class TimelineTag(View):
    template_name = "timeline.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']

        data_list = MessageCard.objects.filter(tag__id=pk)
        size = data_list.count()
        if size > 10:
            data_list = data_list[:10]
        context = {
            "page_tag_id": pk,
            "pages": math.ceil(size / 10),
            "message_card_list": data_list,
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

        data_list = MessageCard.objects.filter(tag__id=pk)
        size = data_list.count()
        if size > 10:
            data_list = data_list[:10]
        context = {
            "page_tag_id": pk,
            "pages": math.ceil(size / 10),
            "message_card_list": data_list,
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


class SearchView(View):
    template_name = "search.html"

    def get(self, request, *args, **kwargs):
        context = {
            "before_search": True,
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        search_type = {"value": request.POST["search_type"]}
        search_key = {"value": request.POST["search_key"]}
        context = {
            "search_type": search_type,
            "search_key": search_key,
        }
        if search_type["value"] == "user":
            if search_key["value"] == "":
                context["search_key"]["error"] = True
            elif len(re.findall(r'[^\w\s\-~ㄱ-ㅎ가-힣ㅏ-ㅣ]', search_key["value"])) > 0:
                context["search_key"]["error"] = True
            else:
                search_keys = [key.strip() for key in search_key["value"].strip().split()]
                search_text = '+'.join(search_keys)
                return redirect("search_user", search_key=search_text)
        elif search_type["value"] == "tag":
            if search_key["value"] == "":
                context["search_key"]["error"] = True
            elif len(re.findall(r'[^\w\s\-~ㄱ-ㅎ가-힣ㅏ-ㅣ]', search_key["value"])) > 0:
                context["search_key"]["error"] = True
            else:
                search_keys = [key.strip() for key in search_key["value"].strip().split()]
                search_text = '+'.join(search_keys)
                return redirect("search_tag", search_key=search_text)
        else:
            context["search_type"]["error"] = True
        return render(request, self.template_name, context=context)


class SearchUser(View):
    template_name = "search.html"

    def get(self, request, *args, **kwargs):
        try:
            search_keys = kwargs['search_key']
        except KeyError:
            return redirect("search")
        search_keys = [key.strip() for key in search_keys.split("+")]
        data_list = User.objects.filter(
            (reduce(operator.and_, (Q(username__contains=key) for key in search_keys))) or
            (reduce(operator.and_, (Q(nickname__contains=key) for key in search_keys)))
        )
        context = {
            "search_type": {"value": "user"},
            "search_key": {"value": ' '.join(search_keys)},
            "user_list": data_list,
        }
        return render(request, self.template_name, context=context)


class SearchTag(View):
    template_name = "search.html"

    def get(self, request, *args, **kwargs):
        try:
            search_keys = kwargs['search_key']
        except KeyError:
            return redirect("search")
        search_keys = [key.strip() for key in search_keys.split("+")]
        data_list = Tag.objects.filter(
            reduce(operator.and_, (Q(name__contains=key) for key in search_keys))
        ).annotate(m_count=Count("tag_message")).order_by("-m_count")
        context = {
            "search_type": {"value": "tag"},
            "search_key": {"value": ' '.join(search_keys)},
            "tag_list": data_list,
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


@require_POST
def load_new_content(request):
    here_path = request.POST.get('here_path', None)
    data_type = request.POST.get('data_type', None)
    pk = request.POST.get('pk', None)
    page = int(request.POST.get('page', None))

    if data_type == "feed":
        feed_user = User.objects.get(id=pk)
        message_card_list = MessageCard.objects.filter(
            Q(author__id=pk) | Q(link_user__id=pk) | Q(forward_user__id=pk) |
            Q(author__in=feed_user.follow.all()) | Q(forward_user__in=feed_user.follow.all())
        )
    elif data_type == "user":
        message_card_list = MessageCard.objects.filter(
            Q(author__id=pk) | Q(link_user__id=pk) | Q(forward_user__id=pk)
        )
    else:
        message_card_list = MessageCard.objects.filter(tag__id=pk)

    size = message_card_list.count()
    if size > page * 10:
        message_card_list = message_card_list[(page - 1) * 10:page * 10]
    elif size > (page - 1) * 10:
        message_card_list = message_card_list[(page - 1) * 10:size]
    else:
        message_card_list = []

    data_list = []
    for message_card in message_card_list:
        data = '''
            <div class="col">
                <div class="card">
        '''
        if message_card.head_image:
            data += f'''
                    <img src="{ message_card.head_image.url }" class="card-img-top" alt="message card head image">
            '''
        data += f'''
                    <div class="card-body">
                        <h5 class="card-title" style="display: inline">{ message_card.author.nickname }</h5>
                        <h6 class="card-subtitle" style="display: inline"><small class="text-muted"><a href="/user/{ message_card.author.username }/"> @{ message_card.author.username }</a></small></h6>
        '''
        if request.user.is_authenticated and request.user != message_card.author:
            data += f'''
                            <span style="float: right"><a href="" class="follow_button" id="follow_button_{ message_card.id }">
            '''
            if message_card.author in request.user.follow.all():
                data += f'''
                                    <i class="fa-solid fa-heart ms-3 me-1"></i>
                '''
            else:
                data += f'''
                                    <i class="fa-regular fa-heart ms-3 me-1"></i>
                '''
            data += f'''
                            </a></span>
            '''
        elif request.user.is_authenticated and request.user == message_card.author:
            data += f'''
                            <span style="float: right">
                                <small class="text-muted" style="word-spacing: 15px">
                                        <a href="#collapse{ message_card.id }" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="collapse{ message_card.id }">수정</a>
                                        <a href="#delete{ message_card.id }" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="delete{ message_card.id }">삭제</a>
                                </small>
                            </span>
            '''
        text = message_card.linked_text().replace("\n", "<br>")
        data += f'''
                        <p class="card-text"><small class="text-muted">{ message_card.created_at.strftime('%Y년 %m월 %d일 %H시 %M분') }</small></p>
                        <p class="card-text">{ text }</p>
                        <p class="card-text">
                            <a href="/message/{ message_card.id }/"><i class="fa-solid fa-comment me-1"></i> { message_card.reply_set.count() }</a>
        '''
        if request.user.is_authenticated and request.user != message_card.author:
            data += f'''
                                <a href="" class="like_button" id="like_button_{ message_card.id }">
            '''
            if request.user in message_card.like_user.all():
                data += f'''
                                        <i class="fa-solid fa-heart ms-3 me-1"></i> { message_card.like_user.count() }
                '''
            else:
                data += f'''
                                        <i class="fa-regular fa-heart ms-3 me-1"></i> { message_card.like_user.count() }
                '''
            data += f'''
                                </a>
            '''
        else:
            data += f'''
                                <i class="fa-regular fa-heart ms-3 me-1"></i> { message_card.like_user.count() }
            '''
        if request.user.is_authenticated and request.user != message_card.author:
            data += f'''
                                <a href="" class="forward_button" id="forward_button_{ message_card.id }">
            '''
            if request.user in message_card.forward_user.all():
                data += f'''
                                        <i class="fa-solid fa-share-from-square ms-3 me-1"></i> { message_card.forward_user.count() }
                '''
            else:
                data += f'''
                                        <i class="fa-regular fa-share-from-square ms-3 me-1"></i> { message_card.forward_user.count() }
                '''
            data += f'''
                                </a>
            '''
        else:
            data += f'''
                                <i class="fa-regular fa-share-from-square ms-3 me-1"></i> { message_card.forward_user.count() }
            '''
        data += f'''
                        </p>
                    </div>
        '''
        text = message_card.content
        if request.user.is_authenticated and request.user == message_card.author:
            data += f'''
                        <div class="card-body collapse" id="collapse{ message_card.id }">
                            <form class="new_form_{ page }" action="{ here_path }" method="post" enctype="multipart/form-data">
                                <div class="btn-group d-none" role="group" aria-label="Basic radio toggle button group">
                                    <input type="radio" class="btn-check" name="form_type" value="modify_message" id="modify_message_{ message_card.id }" autocomplete="off" checked>
                                    <label class="btn btn-outline-primary" for="modify_message_{ message_card.id }">작성</label>
                                </div>
                                <div class="btn-group d-none" role="group" aria-label="Basic radio toggle button group">
                                    <input type="radio" class="btn-check" name="form_id" value="{ message_card.id }" id="modify_message_target_{ message_card.id }" autocomplete="off" checked>
                                    <label class="btn btn-outline-primary" for="modify_message_target_{ message_card.id }">작성</label>
                                </div>
                                <div class="input-group input-group-sm mb-1">
                                    <label class="input-group-text" for="form_image_{ message_card.id }">이미지 파일</label>
                                    <input type="file" class="form-control" name="head_image" id="form_image_{ message_card.id }" accept="image/jpeg, image/png">
                                </div>
                                <div class="input-group">
                                    <span class="input-group-text">메시지 입력</span>
                                    <textarea class="form-control" name="content" id="form_message_{ message_card.id }" aria-label="With textarea" style="height: 100px">{ text }</textarea>
                                    <button class="btn btn-outline-primary" type="submit">수정</button>
                                </div>
                            </form>
                        </div>

                        <div class="card-body collapse" id="delete{ message_card.id }">
                            <form class="new_form_{ page }" id="delete_form_{ message_card.id }" action="{ here_path }" method="post" enctype="multipart/form-data">
                                <div class="btn-group d-none" role="group" aria-label="Basic radio toggle button group">
                                    <input type="radio" class="btn-check" name="form_type" value="delete_message" id="delete_message_{ message_card.id }" autocomplete="off" checked>
                                    <label class="btn btn-outline-primary" for="delete_message_{ message_card.id }">작성</label>
                                </div>
                                <div class="btn-group d-none" role="group" aria-label="Basic radio toggle button group">
                                    <input type="radio" class="btn-check" name="form_id" value="{ message_card.id }" id="delete_message_target_{ message_card.id }" autocomplete="off" checked>
                                    <label class="btn btn-outline-primary" for="delete_message_target_{ message_card.id }">작성</label>
                                </div>
                                <div class="alert alert-danger" role="alert">
                                    정말 삭제할까요?
                                    <span style="float: right"><a href="javascript:document.getElementById('delete_form_{ message_card.id }').submit();">예</a></span>
                                </div>
                            </form>
                        </div>
            '''
        data += f'''
                </div>
            </div>
        '''
        data_list.append(data)

    context = {
        "data_list": data_list
    }
    return HttpResponse(json.dumps(context), content_type="application/json")
