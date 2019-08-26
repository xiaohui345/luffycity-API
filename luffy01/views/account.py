# -*- coding: utf-8 -*-
# @Author: 曾辉
'''
这个模块是关于用户操作的类，比如登录，注册等。
'''

import uuid

from rest_framework.views import APIView
from rest_framework.response import Response

from luffy01.models import Userinfo, Tokeninfo
from luffy01.utils.response_ret import BaseResponse


class Login(APIView):

	'''
	用于用户登录
	'''
	# def options(self, request, *args, **kwargs):
	# 当跨域是复杂请求的时候，浏览器先给你发送一个options预检的请求，
	# 然后预检通过后再给你发送你实际要发送的请求(post),
	# 因此还必须带着Access-Control-Allow-Origin请求头，让你请求通过。这样麻烦才写到中间件去。
	# 预检实际上就是检查你的请求头上是否有
	# 允许你的域名来获取我的数据
	# response["Access-Control-Allow-Origin"] = "*"
	#
	# 允许你携带CONTENT-Type请求头
	# response['Access-Control-Allow-Headers'] = 'Content-Type'
	# 允许你发送DELETE,PUT
	# response['Access-Control-Allow-Methods'] = 'DELETE,PUT'
	# return Response
	def post(self, request, *args, **kwargs):
		# 实例化一个响应的对象.
		ret = BaseResponse()
		try:
			user = Userinfo.objects.filter(**request.data).first()
			# user = Userinfo.objects.get(**request.data)

			# if user:
			# 	token = str(uuid.uuid4())
			# 	# 没有就创建，有就更新;
			# 	Tokeninfo.objects.update_or_create(user=user, defaults={"tokens": token})
			# 	ret["data"]["token"] = token
			# 	ret["data"]["nickname"] = user.nickname
			# else:
			# 	ret["code"] = 10001
			# 	ret["erorr"] = "账号或密码错误"

			# 简单代码往上放.
			#简洁
			if not user:
				ret.code= 10001
				ret.erorr = "账号或密码错误"
				return Response(ret.dict)
			token = str(uuid.uuid4())
			# 没有就创建，有就更新;
			Tokeninfo.objects.update_or_create(user=user, defaults={"tokens": token})
			ret.data["token"] = token
			ret.data["nickname"] = user.nickname
		except Exception as e:
			# 发生异常，需要捕获异常
			ret.code = 10003
			ret.erorr = "错误"
		return Response(ret.dict)


class register(APIView):
	'''
	用户注册
	'''
	def post(self, request, *args, **kwargs):

		ret = {
			"code": 1000,
			"data": {"token": '',
			         'nickname': '', }
		}

		# print(request.data)
		try:
			user = Userinfo.objects.create(**request.data)
			if user:
				token = str(uuid.uuid4())
				# 没有就创建，有就更新;
				Tokeninfo.objects.update_or_create(user=user, defaults={"tokens": token})
				ret["data"]["token"] = token
				ret["data"]["nickname"] = user.nickname
			else:
				ret["code"] = 1001
				ret["erorr"] = "账号不可用"
		except Exception as e:
			ret["code"] = 1002
			ret["erorr"] = e
		return Response(ret)
