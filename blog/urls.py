from django.urls import path
from . import views as mv

app_name = 'blog'

urlpatterns = [
    # 这个视图函数已被基于类的视图取代
    # path('', mv.post_list, name='post_list'),
    path('', mv.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', mv.post_detail,
         name='post_detail'),
    path('<int:post_id>/share/', mv.post_share, name='post_share'),
]
