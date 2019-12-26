from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


# 该函数已被上面基于类的视图取代
def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)  # 每页展示三条post
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # 如果页码超过最大值，则跳至最后一页
        posts = paginator.page(paginator.num_pages)  # 得到总页数
    return render(request, 'blog/post/list.html', {'posts': posts, 'page': page})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # 处理评论内容
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # 将用户提交的数据填入表单
        comment_form = CommentForm(data=request.POST)
        # 验证表单有效性
        if comment_form.is_valid():
            # 通过调用save()实例化Comment模型对象,但暂不保存至数据库，
            # 方便后续修改，避免反复提交
            new_comment = comment_form.save(commit=False)
            # 将评论与当前文章绑定
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post/detail.html',
                  {'post': post,
                   'comment_form': comment_form,
                   'new_comment': new_comment,
                   'comments': comments})


def post_share(request, post_id):
    """通过邮件发送id为post_id的文章"""
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():  # 验证表单有效性(不检测表单数据)
            cd = form.cleaned_data  # 仅保留有效的表单数据
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) 推荐你阅读"{}"'.format(cd['name'], cd['email'], post.title)
            message = '在{}查看{}\n\n{}的评论:{}'\
                .format(post_url, post.title, cd['name'], cd['comments'])
            send_mail(subject, message, '1520966793@qq.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
