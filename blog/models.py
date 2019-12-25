from django.db import models

from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class PublishedManager(models.Manager):
    # 重写get_queryset方法，增加过滤功能
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):

    objects = models.Manager()
    published = PublishedManager()
    # 用于设置status
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    # slug 用于为每条post创建优雅的urls
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')  # 根据发布时间创建每条post的url
    # 指定post的作者user，这里是多对一的关系
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,  # 当user被删除时，其发布的post也将被删除
                               related_name='blog_posts')  # 指定逆向关系的名称，即user.blog_posts
    body = models.TextField()
    # 发布时间
    publish = models.DateTimeField(default=timezone.now)
    # 创建时间
    created = models.DateTimeField(auto_now_add=True)  # 创建时自动记录
    # 最近一次更新的时间
    updated = models.DateTimeField(auto_now=True)  # 保存时自动记录
    # 设置该post的状态
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='draft')

    # 按时间顺序排列posts，最近发表的在最上面
    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])
