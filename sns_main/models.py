from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import re


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^[\w-]+\Z'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and +/-/_ characters.'
    )
    flags = 0


class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and -/_ only.'),
        validators=[UsernameValidator()],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    nickname = models.CharField(max_length=50)
    follow = models.ManyToManyField('self', blank=True, related_name='follower')

    def __str__(self):
        return self.nickname + ' @' + self.username


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/tag/{self.slug}/'


class MessageCard(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content = models.TextField()
    head_image = models.ImageField(upload_to=f'images/{author.__hash__()}/', blank=True)

    tag = models.ManyToManyField(Tag, related_name='tag_message', blank=True)
    link_user = models.ManyToManyField(User, related_name='link_message', blank=True)
    like_user = models.ManyToManyField(User, related_name='like_message', blank=True)
    forward_user = models.ManyToManyField(User, related_name='forward_message', blank=True)

    def __str__(self):
        return f'{self.pk} @{self.author} created at {self.created_at}, updated at {self.updated_at}'

    def get_absolute_url(self):
        return f'/message/{self.pk}/'

    def get_link_users(self):
        r = re.compile(r"@([\w\-]+)")
        linked_usernames = r.findall(self.content)
        try:
            return User.objects.filter(username__in=linked_usernames)
        except User.DoesNotExist:
            return None

    def get_tags(self):
        r = re.compile(r"#([\w+*%~\-=/\\\^|&!]+)")
        linked_tags = r.findall(self.content)
        try:
            return Tag.objects.filter(name__in=linked_tags)
        except Tag.DoesNotExist:
            return None

    def linked_text(self):
        linkable_users = self.get_link_users()
        linkable_tags = self.get_tags()
        link = {f"@{user.username}": f"<a href='/user/{user.username}/'>@{user.username}</a>" for user in linkable_users}
        link.update(
            {f"#{tag.name}": f"<a href='/tag/{tag.slug}/'>#{tag.name}</a>" for tag in linkable_tags}
        )
        text = self.content
        for elm in link:
            print("elm:", elm)
            text = text.replace(elm, link[elm])
        print("text:", text)
        return text

    class Meta:
        ordering = ["created_at"]


class Reply(models.Model):
    message = models.ForeignKey(MessageCard, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content = models.TextField()

    def __str__(self):
        return f'{self.pk} @{self.author} created at {self.created_at}, updated at {self.updated_at}'

    class Meta:
        ordering = ["created_at"]
