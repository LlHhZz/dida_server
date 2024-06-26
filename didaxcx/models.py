from django.db import models
from django.contrib.auth.models import User

'''
python3 manage.py makemigrations didaxcx
python3 manage.py migrate didaxcx
'''

class Participant(models.Model):
    openid = models.CharField(max_length=255) # OpenId 唯一标识符
    username = models.CharField(max_length=255) # 同样的唯一标识符 自动生成 可修改
    photo = models.URLField(max_length=255, blank=True) # 头像 自动提供 可修改
    phone = models.CharField(max_length=255) # 关联手机号 作为手机号登录关联的依据
    gender = models.CharField(max_length=255) # 用户的性别
    age = models.IntegerField(default=20) # 用户的年龄
    description = models.CharField(max_length=255) # 孩子身份描述 根据选择组合 x岁x孩家长
    role = models.CharField(max_length=255, default='家长') # 用户身份 家长 性教育讲师 性教育关注者
    childsex = models.CharField(max_length=255) # 孩子性别 男女
    childage = models.IntegerField(default=5) # 孩子年龄

    def __str__(self):
        return str(self.user)

class StoryBank(models.Model):
    # 故事库 
    # 1. 部位（脑袋，脸部，肩部，胸部，腹部，臀部，阴部，腿部，脚部）
    # 2. 颜色（绿，黄，红）
    # 3. 主题（权力与价值观，性与性行为，关系，文化和性，人体和发育，暴力和安全保障，理解性别，性与生殖健康）
    body = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default='')
    # 故事内容（以\n换行分段）
    content = models.CharField(max_length=2047)

class QuestionAnswerBank(models.Model):
    # 问答库
    # 1. 问题（文字表述）
    # 2. 适龄段（）
    # 3. 分词
    question = models.CharField(max_length=2047)
    ageGroup = models.CharField(max_length=255)
    keyWord = models.CharField(max_length=2047)
    # 回答内容
    answer = models.CharField(max_length=2047)

# 好像不需要
class ViewedStory(models.Model):
    # 浏览过的故事 
    
    # openid用户 -> storyid故事
    openid = models.CharField(max_length=255) # OpenId 唯一标识符
    storyid = models.IntegerField(default=0) # 关联到的Story
    # 喜欢收藏的故事
    collected = models.BooleanField(default=False)  # 是否喜欢收藏了该故事

class CollectedStory(models.Model):
    # 喜欢收藏的故事
    # openid用户 -> storyid故事
    openid = models.CharField(max_length=255) # OpenId 唯一标识符
    storyid = models.IntegerField(default=0) # 关联到的Story 唯一标识符