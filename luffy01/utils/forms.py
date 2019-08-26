# -*- coding: utf-8 -*-
# @Author: 曾辉

#分页
from rest_framework import  exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import BaseAuthentication

from luffy01.models import Tokeninfo

class MyPageNumberPagination(PageNumberPagination):

	page_size = 2
	page_query_param = 'page'  #get请求的页面参数

	page_size_query_param = 'size'  # 临时每页的数量 size=4
	max_page_size = 5  # 临时每页的最大数量


# BasicAuthentication  #基于浏览器进行认证，浏览器弹框
class UserAuthentication(BaseAuthentication):

	def authenticate(self,request):
		token = request.GET.get("token")
		token_obj = Tokeninfo.objects.filter(tokens=token).first()
		if not token_obj:
			raise exceptions.AuthenticationFailed("用户认证失败")
		else:
			return (token_obj.user.id,token_obj.tokens)
			#         request.user, request.auth