from django import forms
from django.contrib.auth.hashers import make_password
from .models import *


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error('password', '잘못된 비밀번호입니다.')
        except User.DoesNotExist:
            self.add_error('username', '존재하지 않는 id입니다.')


class RegisterForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    re_password = forms.CharField()
    nickname = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        re_password = cleaned_data.get('re_password')
        nickname = cleaned_data.get('nickname')

        chk = True

        try:
            User.objects.get(username=username)
            self.add_error('username', '이미 존재하는 id입니다.')
        except User.DoesNotExist:
            for letter in str(username).lower():
                if not ('a' <= letter <= 'z' or '1' <= letter <= '9' or letter in '-_'):
                    self.add_error('username', '잘못된 id입니다.')
                    chk = False

        try:
            User.objects.get(nickname=nickname)
            self.add_error('nickname', '이미 존재하는 닉네임입니다.')
        except User.DoesNotExist:
            for letter in str(nickname).lower():
                if letter == ' ':
                    self.add_error('nickname', '잘못된 닉네임입니다.')
                    chk = False

        if password and re_password:
            if password != re_password:
                self.add_error('re_password', '비밀번호 확인이 일치하지 않습니다.')
            elif chk:
                user = User(
                    username=username,
                    password=make_password(password),
                    nickname=nickname
                )
                user.save()
        else:
            self.add_error('password', '잘못된 비밀번호입니다.')


# class TimelineForm(forms.Form):
#     form_type = forms.CharField()
#     form_image = forms.ImageField(allow_empty_file=True)
#     form_message = forms.CharField(widget=forms.Textarea)
#
#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop("user")
#         super(TimelineForm, self).__init__(*args, **kwargs)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         form_type = cleaned_data.get("form_type")
#         form_image = cleaned_data.get("form_image")
#         form_message = cleaned_data.get("form_message")
#
#         if str(form_type) == "insert_message":
#             if form_message:
#                 if form_image:
#                     new_message = MessageCard(
#                         author=self.user,
#                         head_image=form_image,
#                         content=form_message,
#                     )
#                 else:
#                     new_message = MessageCard(
#                         author=self.user,
#                         content=form_message,
#                     )
#                 new_message.save()
#                 linked_users = new_message.get_link_users()
#                 if linked_users:
#                     new_message.link_user.set(new_message.get_link_users())
#                 tags = new_message.get_tags()
#                 addable_tags = new_message.get_addable_tags()
#                 if tags:
#                     for tag in tags:
#                         new_message.tag.add(tag)
#                 if addable_tags:
#                     for tag in addable_tags:
#                         Tag(name=tag).save()
#                         new_tag = Tag.objects.get(name=tag)
#                         new_message.tag.add(new_tag)
#                 return self.cleaned_data
#             else:
#                 self.add_error("form_message", "메시지가 비어있습니다.")
#                 print("메시지가 비어있습니다.")
#         elif str(form_type).startswith("modify_message"):
#             for _ in [0]:
#                 try:
#                     target_message = MessageCard.objects.get(id=int(str(form_type).replace("modify_message_", "")))
#                 except ValueError:
#                     self.add_error("form_type", "대상 메시지 ID를 읽을 수 없습니다.")
#                     print("대상 메시지 ID를 읽을 수 없습니다.")
#                     break
#                 except MessageCard.DoesNotExist:
#                     self.add_error("form_type", "대상 메시지가 존재하지 않습니다.")
#                     print("대상 메시지가 존재하지 않습니다.")
#                     break
#                 if form_image:
#                     target_message.head_image = form_image
#                 if target_message.content != form_message:
#                     target_message.content = form_message
#                 target_message.save()
#                 linked_users = target_message.get_link_users()
#                 if linked_users:
#                     target_message.link_user.set(target_message.get_link_users())
#                 tags = target_message.get_tags()
#                 addable_tags = target_message.get_addable_tags()
#                 target_message.tag.clear()
#                 if tags:
#                     for tag in tags:
#                         target_message.tag.add(tag)
#                 if addable_tags:
#                     for tag in addable_tags:
#                         Tag(name=tag).save()
#                         new_tag = Tag.objects.get(name=tag)
#                         target_message.tag.add(new_tag)
#                 return self.cleaned_data
#         else:
#             self.add_error("form_type", "잘못된 요청입니다.")
#             print("잘못된 요청입니다.")

class TimelineForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TimelineForm, self).__init__(*args, **kwargs)
        self.fields['head_image'].required = False

    class Meta:
        model = MessageCard
        fields = ('head_image', 'content')
