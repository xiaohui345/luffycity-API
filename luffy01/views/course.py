# -*- coding: utf-8 -*-
# @Author: 曾辉

# 对字段进行操作，需要用F包起来；
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from rest_framework.viewsets import ModelViewSet, ViewSetMixin

from luffy01 import models
from luffy01.serializers.course import CouserSerializers, CourseDetailViewSerializers, ArticleSerializers, \
	ArticledetialSerializers
from luffy01.utils.response_ret import BaseResponse, DataResponse
from luffy01.utils.forms import UserAuthentication


# 简单的单表操作，可以直接用ModelViewSet，里面的类所继承的方法，不需要自己写了
class CourseView(ModelViewSet):
	'''
	与课程相关的操作
	'''

	# 分页 GenericAPIView这个类里面才有分页器
	# pagination_class = MyPageNumberPagination
	# 获取数据
	# queryset = models.Course.objects.all()
	# 序列化器
	# serializer_class = CouserSerializers
	def list(self, request, *args, **kwargs):
		'''
		课程API
		:param request:
		:param args:
		:param kwargs:
		:return:
		'''
		ret = BaseResponse()
		try:
			cobj = models.Course.objects.all()
			qureyset = CouserSerializers(instance=cobj, many=True)
			ret.data = qureyset.data
		except Exception as e:
			ret.code = 1002
			ret.error = e
		return Response(ret.dict)

	def retrieve(self, request, *args, **kwargs):
		'''
		课程详细API
		:param request:
		:param args:
		:param kwargs:
		:return:
		'''
		ret = DataResponse()
		try:
			c_pk = kwargs.get('pk')
			# 这里的ID是课程ID
			cdobj = models.CourseDetail.objects.filter(course__id=c_pk).first()
			qureyset = CourseDetailViewSerializers(instance=cdobj, many=False)
			print(qureyset.data)

			ret.data.append(qureyset.data)
		except  Exception as e:
			ret.code = 1002
			ret.error = "错误"
		print(ret.dict)
		return Response(ret.dict)


class MicroView(ViewSetMixin, APIView):
	'''
	与深科技相关的
	'''
	# 用户认证
	authentication_classes = [UserAuthentication]

	def list(self, request, *args, **kwargs):
		'''
		文章列表
		:param request:
		:param args:
		:param kwargs:
		:return:
		'''
		ret = DataResponse()
		try:
			article_list = models.Article.objects.all()
			qureyset = ArticleSerializers(article_list, many=True)
			ret.data = qureyset.data
		except  Exception as e:
			ret.code = 1002
			ret.error = "错误"
		return Response(ret.dict)

	def retrieve(self, request, *args, **kwargs):
		'''
		文章详细
		:param request:
		:param args:
		:param kwargs:
		:return:
		'''
		ret = DataResponse()
		try:
			arctile_id = kwargs.get('pk')
			article_obj = models.Article.objects.filter(id=arctile_id).first()
			# 得到关于这个文章的所有评论
			arcticle_comment = []
			for item in article_obj.Comment_list.all():
				# 区别一下哪些是子评论和 根评论
				try:
					p_id = item.p_node.id
					# 父评论的数据
					p_comment = {
						"username": item.p_node.account.nickname,
						'comment': item.p_node.content
					}
				except Exception:
					p_id = False
					p_comment = {}
				arcticle_comment.append({"id": item.id, "username": item.account.nickname, "comment": item.content,
				                         "disagree_number": item.disagree_number,
				                         "agree_number": item.agree_number, "date": item.date, "p_id": p_id,
				                         "p_comment": p_comment})
			qureyset = ArticledetialSerializers(article_obj, many=False)
			ret.data = qureyset.data
			ret.comment = arcticle_comment
		except Exception as e:
			ret.code = 1002
			ret.error = "错误"
		return Response(ret.dict)

	def create(self, request, *args, **kwargs):
		'''
		创建文章的评论
		:param request:
		:param args:
		:param kwargs:
		:return:
		'''
		ret = DataResponse()
		try:
			article_id = request.data.get("article_id")
			# 要添加的具体的对象
			arctile_obj = models.Article.objects.filter(id=article_id).first()
			content = request.data.get("comentcontent")
			tokens = request.data.get("token")
			account = models.Tokeninfo.objects.filter(tokens=tokens).first().user
			# 父评论的ID
			p_node = request.data.get("p_node")
			print(account, arctile_obj)
			if p_node:
				# 子评论
				# 先找到'\n'的索引位置
				nindex = content.index('\n')
				# 那'\n'的索引位置的后面的数据才是真正的内容。
				new_content = content[nindex + 1:]
				comment_obj = models.Comment.objects.create(content_object=arctile_obj, content=new_content,
				                                            account=account, p_node_id=p_node)
			else:
				# 根评论
				# 生成评论记录
				comment_obj = models.Comment.objects.create(content_object=arctile_obj, content=content,
				                                            account=account)

			ret.comment = {"username": account.nickname, "comment": content, "date": comment_obj.date}
			ret.msg = '评论成功'
		except Exception:
			ret.code = 1001
			ret.error = '评论失败'

		return Response(ret.dict)


class UpdownView(APIView):
	'''
	点赞和踩
	'''

	def post(self, request, *args, **kwargs):
		ret = BaseResponse()
		article_id = request.data.get("article_id")
		arctile_obj = models.Article.objects.filter(id=article_id).first()
		tokens = request.data.get("token")
		account = models.Tokeninfo.objects.filter(tokens=tokens).first().user
		isUp = request.data.get("isup")  # 已经反序列化为true了
		# print(isUp)
		# 事务  原子性操作(要么同时执行，要么都不执行) mysql
		try:
			models.ArticleUpDown.objects.create(article=arctile_obj, user=account, is_up=isUp)
			if isUp:
				# 表示点赞数
				models.Article.objects.filter(pk=article_id).update(agree_num=F("agree_num") + 1)
			# 否则是踩数加1
			# else:
			# 	Article.objects.filter(pk=article_id).update(up_count=F("agree_num") + 1)
			ret.status = True
		except Exception:
			# 已经点赞过了
			ret.status = False
			# 如果有点赞或是踩的时候需要判断一下，用户第一次的操作，是点赞还是踩，然后才返回提示（点赞过或是踩过）在这么只有点赞，所以没有补充
			ret.msg = "已经点赞过了"
		return Response(ret.dict)


class CollectionView(APIView):
	'''
	收藏
	'''

	def post(self, request, *args, **kwargs):

		ret = BaseResponse()

		article_id = request.data.get("article_id")
		arctile_obj = models.Article.objects.filter(id=article_id).first()
		tokens = request.data.get("token")
		account = models.Tokeninfo.objects.filter(tokens=tokens).first().user

		try:
			# 收藏成功
			models.Collection.objects.create(content_object=arctile_obj, account=account)
			# 收藏数加1
			models.Article.objects.filter(pk=article_id).update(collect_num=F("collect_num") + 1)
			ret.status = True
			ret.msg = "收藏成功"

		except Exception:
			# 这里报错就相当于在点击了一次收藏，即取消收藏
			models.Article.objects.filter(pk=article_id).update(collect_num=F("collect_num") - 1)
			str_model = models.Article._meta.model_name
			models.Collection.objects.filter(content_type=ContentType.objects.get(model=str_model),
			                                 object_id=article_id, account=account).delete()
			ret.msg = "取消收藏"
			ret.status = False

		return Response(ret.dict)
