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


class UserModifyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserModifyForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('nickname', )


class TimelineForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TimelineForm, self).__init__(*args, **kwargs)
        self.fields['head_image'].required = False

    class Meta:
        model = MessageCard
        fields = ('head_image', 'content')


class ReplyForm(forms.ModelForm):
    def __init__(self, user, message, *args, **kwargs):
        self.user = user
        self.message = message
        super(ReplyForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Reply
        fields = ('content', )
