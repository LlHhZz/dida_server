from django.http import JsonResponse

import jwt
import requests
import json
import csv
from django.conf import settings
from datetime import datetime, timedelta

from .models import Participant, StoryBank, CollectedStory, QuestionAnswerBank

def generate_token(openid):
    # 设置过期时间为 1 小时
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    # 构建 payload，包含用户标识 openid 和过期时间 exp
    payload = {
        'openid': openid,
        'exp': expiration_time
    }

    # 使用 JWT 签名生成 Token
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    return token

import random
import string
def generate_random_username(letter_num = 5, digit_num = 5):
    letters = string.ascii_letters
    digits = string.digits
    random_letters = ''.join(random.choice(letters) for _ in range(letter_num))
    random_digits = ''.join(random.choice(digits) for _ in range(digit_num))
    random_username = random_letters + random_digits
    return random_username

def wechat_login(request):
    if request.method == 'POST':
        # request.POST.get('') 只适用于 application/x-www-form-urlencoded 或 multipart/form-data 类型的表单数据
        # 利用Json传入的数据 需要使用request.body获取
        data = json.loads(request.body.decode('utf-8'))
        code = data.get('code')  # 从前端请求中获取微信登录凭证

        # 调用微信登录 API，获取用户信息
        wechat_api_url = 'https://api.weixin.qq.com/sns/jscode2session'
        params = {
            'appid': 'wx9d0c15657a3dbc25',
            'secret': '2f1ce1d6748ac2c8ee3458d8a803c908',
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.get(wechat_api_url, params=params)
        data = response.json()

        # 处理微信登录结果
        if 'openid' in data and 'session_key' in data:
            # 唯一标识符
            openid = data['openid']
            session_key = data['session_key']
            
            # 根据唯一标识符openid查找用户信息 若未查到则新建用户记录
            user = Participant.objects.filter(openid=openid)
            
            if not user:
                # 生成随机用户名
                random_username = generate_random_username()
                # 创建记录
                new_participant = Participant.objects.create(
                    openid=openid,
                    username=random_username,
                    photo='https://cdn.acwing.com/media/user/profile/photo/259412_lg_973f7b076d.jpg',
                    phone='',
                    gender='',
                    description='',
                    childsex=''
                )
                new_participant.save()

            # 生成用户登录凭证（Token）
            token = generate_token(openid)  # 自定义函数，用于生成用户登录凭证

            # 返回响应
            return JsonResponse({
                'result': 'success',
                'openid': openid,
                'token': token,
            })
        else:
            return JsonResponse({
                'result': 'failed', 
                'error': 'Failed to login with WeChat'
            })
    else:
        return JsonResponse({
            'result': 'failed',
            'error': 'Invalid request method'
        })

def user_info(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        openid = data.get('openid')

        if openid:
            # 根据唯一标识符openid查找用户信息
            user = Participant.objects.get(openid=openid)
            if user:
                # 返回响应
                return JsonResponse({
                    'result': 'success',
                    'openid': user.openid,
                    'username': user.username,
                    'photo': user.photo,
                    'phone': user.phone,
                    'gender': user.gender,
                    'age': user.age,
                    'description': user.description,
                    'role': user.role,
                    'childsex': user.childsex,
                    'childage': user.childage,
                })
            else:
                return JsonResponse({
                    'result': 'failed', 
                    'error': 'Failed to get userInfo'
                })
        else:
            return JsonResponse({
                'result': 'failed',
                'error': 'Invalid request method'
            })

def modify_username(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        openid = data.get('openid')
        username = data.get('username')

        if openid and username:
            # 根据唯一标识符openid查找用户信息
            try:
                # 根据唯一标识符 openid 查找用户信息
                user = Participant.objects.get(openid=openid)
                # 更新用户的用户名
                user.username = username
                user.save()  # 保存更新后的用户名
                # 返回成功响应
                return JsonResponse({
                    'result': 'success',
                })
            except Participant.DoesNotExist:
                # 如果找不到用户，返回失败响应
                return JsonResponse({
                    'result': 'failed',
                    'error': 'User not found'
                })
        else:
            return JsonResponse({
                'result': 'failed',
                'error': 'Invalid request method'
            })

import base64
from django.core.files.base import ContentFile
def modify_photo(request):
    if request.method == 'POST' and request.FILES.get('file'):
        openid = request.POST.get('openid')
        uploaded_file = request.FILES['file']

        if openid and uploaded_file:
            # 根据唯一标识符openid查找用户信息
            try:
                # 根据唯一标识符 openid 查找用户信息
                user = Participant.objects.get(openid=openid)
                # 将接收到的图片数据保存到服务器的指定目录中
                photo_path = save_photo_to_server(openid, uploaded_file)
                # 更新用户的头像
                user.photo = photo_path
                user.save()  # 保存更新后的用户名
                # 返回成功响应
                return JsonResponse({
                    'result': 'success',
                    'photo_path': photo_path
                })
            except Participant.DoesNotExist:
                # 如果找不到用户，返回失败响应
                return JsonResponse({
                    'result': 'failed',
                    'error': 'User not found'
                })
        else:
            return JsonResponse({
                'result': 'failed',
                'error': 'Invalid request method'
            })

import os
import random
def save_photo_to_server(openid, photo_file):
    # 检查目标目录是否存在，如果不存在则创建它
    target_dir = './media/'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 生成随机数作为标识
    random_identifier = str(random.randint(1000, 9999))

    # 生成保存图片的文件路径
    photo_path = os.path.join(target_dir, 'uploaded_photo_' + openid + '_' + random_identifier + '.jpg')  # 这里假设图片保存为 jpg 格式
    load_path = 'http://43.135.136.2:8000/media/' + 'uploaded_photo_' + openid + '_' + random_identifier + '.jpg'

    # 写入图片数据到文件中
    with open(photo_path, 'wb') as f:
        for chunk in photo_file.chunks():
            f.write(chunk)

    # 返回保存后的图片路径
    return load_path

def modify_roleinfo(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        openid = data.get('openid')
        role = data.get('role')
        childsex = data.get('childsex')
        childage = data.get('childage')
        gender = data.get('sex')
        age = data.get('age')
        description = childage + '岁' + childsex + '孩' + role

        childage = int(childage)
        age = int(age)

        if openid:
            # 根据唯一标识符openid查找用户信息
            try:
                # 根据唯一标识符 openid 查找用户信息
                user = Participant.objects.get(openid=openid)
                # 更新用户的用户名
                user.role = role
                user.childsex = childsex
                user.childage = childage
                user.gender = gender
                user.age = age
                user.description = description

                user.save()  # 保存更新
                # 返回成功响应
                return JsonResponse({
                    'result': 'success',
                })
            except Participant.DoesNotExist:
                # 如果找不到用户，返回失败响应
                return JsonResponse({
                    'result': 'failed',
                    'error': 'User not found'
                })
        else:
            return JsonResponse({
                'result': 'failed',
                'error': 'Invalid request method'
            })

def upload_story(request):
    if request.method == 'POST':
        csv_file = request.FILES['file']
        # 读取上传的CSV文件并将故事内容匹配到数据库中
        csv_data = csv.reader(csv_file.read().decode('gbk').splitlines())
        next(csv_data)  # 跳过表头行

        for row in csv_data:
            body = row[0].strip()
            color = row[1].strip()
            topic = row[2].strip()
            content = row[3].strip()
            title = row[4].strip()

            if content:
                # 根据部位、颜色和主题在数据库中查找相应的记录
                story = StoryBank.objects.filter(body=body, color=color, topic=topic, content=content, title=title).first()
                if not story:
                    # 创建新的故事记录
                    StoryBank.objects.create(body=body, color=color, topic=topic, content=content, title=title)
        return JsonResponse({'message': '文件上传成功'})
    else:
        return JsonResponse({'error': '没有上传文件或请求方法不正确'})

def find_story(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        body = data.get('body')
        color = data.get('color')
        topic = data.get('topic')

        # 根据查询参数进行过滤
        stories = StoryBank.objects.filter(body=body, color=color, topic=topic)

        # 将查询到的数据序列化为字典列表
        data = [{'body': story.body, 'color': story.color, 'topic': story.topic, 'content': story.content, 'title': story.title, 'storyid': story.id} for story in stories]
        # 返回查询结果
        return JsonResponse({
            'result': 'success',
            'data': data
        })
    else:
        return JsonResponse({
            'result': 'failed',
            'error': '请求方法错误'
        })

def collect_or_discollect_story(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        openid = data.get('openid')
        storyid = data.get('storyid')

        # 根据查询参数进行过滤
        collection = CollectedStory.objects.filter(openid=openid, storyid=storyid)
        if collection:
            collection.delete()
            return JsonResponse({
                'result': 'success',
                'message': '取消成功',
            })
        else:
            CollectedStory.objects.create(openid=openid, storyid=storyid)
            return JsonResponse({
                'result': 'success',
                'message': '收藏成功',
            })
    else:
        return JsonResponse({
            'result': 'failed',
            'error': '请求方法错误'
        })

def get_story_collected_state(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        openid = data.get('openid')
        storyid = data.get('storyid')

        # 根据查询参数进行过滤
        collection = CollectedStory.objects.filter(openid=openid, storyid=storyid)
        if collection:
            return JsonResponse({
                'result': 'success',
                'data': 'True',
            })
        else:
            return JsonResponse({
                'result': 'success',
                'data': 'False',
            })
    else:
        return JsonResponse({
            'result': 'failed',
            'error': '请求方法错误'
        })

def get_collected_story(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        openid = data.get('openid')
        body = data.get('body')
        color = data.get('color')
        topic = data.get('topic')

        try:
            # 根据 openid 在 CollectedStory 中查找收藏记录
            collections = CollectedStory.objects.filter(openid=openid)
            
            # 初始化存储结果的列表
            collected_story_info = []
            
            # 遍历每个收藏记录，获取对应的故事信息
            for collection in collections:
                story_info = {}
                
                story = StoryBank.objects.get(id=collection.storyid)
                if (not body or story.body == body) and (not color or story.color == color) and (not topic or story.topic == topic):
                    # 组装故事信息
                    story_info['storyid'] = story.id
                    story_info['body'] = story.body
                    story_info['color'] = story.color
                    story_info['topic'] = story.topic
                    story_info['title'] = story.title
                    story_info['content'] = story.content

                    # 将故事信息添加到结果列表中
                    collected_story_info.append(story_info)
            
            return JsonResponse({
                'result': 'success',
                'collected_stories': collected_story_info
            })
        except CollectedStory.DoesNotExist:
            return JsonResponse({
                'result': 'failed',
                'error': '未找到对应的收藏记录'
            })
    else:
        return JsonResponse({
            'result': 'failed',
            'error': '请求方法错误'
        })

def get_all_story(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        openid = data.get('openid')
        body = data.get('body')
        color = data.get('color')
        topic = data.get('topic')

        try:
            # 在 StoryBank 中获取所有故事
            stories = StoryBank.objects.all()
            
            # 初始化存储结果的列表
            all_story_info = []
            
            # 遍历每个故事，进行判断是否已收藏
            for story in stories:
                if (not body or story.body == body) and (not color or story.color == color) and (not topic or story.topic == topic):
                    # 组装故事信息
                    story_info = {
                        'storyid': story.id,
                        'body': story.body,
                        'color': story.color,
                        'topic': story.topic,
                        'title': story.title,
                        'content': story.content,
                        'collected': 'no',
                    }
                    # 在 CollectedStory 中查找是否有对应的收藏记录
                    if CollectedStory.objects.filter(openid=openid, storyid=story.id).exists():
                        story_info['collected'] = 'yes'
                    # 将故事信息添加到结果列表中
                    all_story_info.append(story_info)
            
            return JsonResponse({
                'result': 'success',
                'collected_stories': all_story_info
            })
        except CollectedStory.DoesNotExist:
            return JsonResponse({
                'result': 'failed',
                'error': '未找到对应的收藏记录'
            })
    else:
        return JsonResponse({
            'result': 'failed',
            'error': '请求方法错误'
        })

import jieba
from jieba import analyse
def upload_question(request):
    # 上传题库，对问题进行分词处理提取关键词，然后保存到数据库中
    if request.method == 'POST':
        csv_file = request.FILES['file']
        # 读取上传的CSV文件并将故事内容匹配到数据库中
        csv_data = csv.reader(csv_file.read().decode('gbk').splitlines())
        next(csv_data)  # 跳过表头行

        for row in csv_data:
            question = row[0]
            answers = row[1:]

            # 确定适龄段
            age_groups = ['0-3岁', '3-6岁', '6-9岁', '9-12岁', '12-15岁']
            age_group = next((age for age, answer in zip(age_groups, answers) if answer.strip()), '')

            # 提取关键词
            keywords = ' '.join(analyse.extract_tags(question, topK=10))
            
            # 对每个答案（问题，适龄段）存入数据库
            for i in range(len(answers)):
                ageGroup = age_groups[i]
                answer = answers[i].strip()
                if answer:
                    record = QuestionAnswerBank.objects.filter(question=question, ageGroup=ageGroup).first()
                    if not record:
                        # 创建新的题库记录
                        QuestionAnswerBank.objects.create(question=question, ageGroup=ageGroup, keyWord=keywords, answer=answer)
        return JsonResponse({'message': '文件上传成功'})
    else:
        return JsonResponse({'error': '没有上传文件或请求方法不正确'})

from django.db import connection
from django.db.models import Q
def get_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        question = data.get('question')
        childage = int(data.get('childage'))

        # 根据年龄分组
        ageGroup = ''
        if childage <= 3:
            ageGroup = '0-3岁'
        elif childage <= 6:
            ageGroup = '3-6岁'
        elif childage <= 9:
            ageGroup = '6-9岁'
        elif childage <= 12:
            ageGroup = '9-12岁'
        elif childage <= 15:
            ageGroup = '12-15岁'

        # 使用 jieba 进行关键词提取 
        keywords = analyse.extract_tags(question, topK=2)

        # 构建查询条件（泛化匹配，只比较关键词）
        query = Q(ageGroup=ageGroup)
        for keyword in keywords:
            query &= Q(keyWord__icontains=keyword)  # 添加多个关键词匹配条件
        
        # 查找数据库中匹配关键词的记录
        answer_record = QuestionAnswerBank.objects.filter(query).first()

        if answer_record:
            # 如果找到了匹配的记录，返回答案
            return JsonResponse({
                'result': 'success',
                'answer': answer_record.answer
            })
        
        # 如果没有找到答案，查找相关的问题
        related_questions = QuestionAnswerBank.objects.filter(query).values_list('question', flat=True)[:3]  # 取最多3个相关问题

        if related_questions:
            return JsonResponse({
                'result': 'onlyquestions',
                'answer': '提供以下这些问题可供选择',
                'questions': list(related_questions)
            })
        else:
            return JsonResponse({
                'result': 'failed',
                'answer': '暂时没有这个问题的回答，你需要向滴答计划反馈，并获得后续回答吗？'
            })