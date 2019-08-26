# -*- coding: utf-8 -*-
# @Author: 曾辉

class BaseResponse():
	'''
	通用返回的响应体
	'''
	def __init__(self):
		self.code = 1000
		self.data = {}
		self.error  = None
	@property
	def dict(self):
		# 把类里面的所有数据按照字典的形式进行封装

		return self.__dict__

class DataResponse(BaseResponse):
	'''
	data数据是列表的响应体
	'''
	def __init__(self):
		self.code = 1000
		self.data=[]
		self.comment = None
		self.msg =None
		self.error = None

