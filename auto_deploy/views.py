# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,render_to_response,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from requests.auth import HTTPBasicAuth
import requests
import jenkins
import configparser
import json
import yaml
import re
import os
import time,datetime
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
# Create your views here.

from django.template import RequestContext
from django import forms
#from .models import User
from django.contrib.auth.models import User
from auto_deploy.models import deploy as deploy_model

def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    if request.method == "POST":
          u = request.POST.get("username")
          p = request.POST.get("password")
          person=User.objects.filter(username__exact=u)
          if not person:
              user = User.objects.create_user(username=u, password=p)
              if user.username == u:
                  return JsonResponse({"status": True, "message": "注册成功"})
          else:
              return JsonResponse({"status": False, "message": "用户已存在"})


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    if request.method == "POST":
          u = request.POST.get("username")
          p = request.POST.get("password")
          person=User.objects.filter(username__exact=u)
          if not person:
              return JsonResponse({"status": False, "message": "用户不存在"})
          user = auth.authenticate(username=u, password=p)
          if user is not None:
              if user.is_active:
                  auth.login(request,user)
                  return JsonResponse({"status": True, "message": "登录成功"})
                 # return redirect('/autodeploy/index/')
              else:
                  return JsonResponse({"status":False,"message":"用户名或密码错误"})
          else:
              return JsonResponse({"status":False,"message":"用户名或密码错误"})



@login_required()
def index(request):
    return render(request,'index.html')



def index_detail(request):
    test=[{'appname':"test1","tag_version":"v0.0.3","status":"up","deployer":"xiaowang"},
          {'appname':"test2","tag_version":"v0.0.4","status":"up","deployer":"xiaoli"},
          {'appname':"test3","tag_version":"v0.0.5","status":"down","deployer":"xiaozhang"}]
    return JsonResponse(test,safe=False)


def index_env(request):
    tablelist=[]
    env = request.GET.get("env")
    cf = configparser.ConfigParser()
    cf.read('auto_deploy/conflist')
    appname = cf.options(env)
    for i in appname:
        try:
            field=deploy_model.objects.filter(appname=i).filter(env=env).order_by("-deploytime")[0]
        except Exception as e:
            tag_version="null"
            deployer="null"
        else:
            tag_version=field.tag_version
            if tag_version == None:
                tag_version = "null"
            deployer=field.deployer
        rowlist={}
        rowlist['appname']=i
        rowlist['tag_version']=tag_version
        rowlist['deployer']=deployer
        rowlist['status']=json.loads(getcertfile(env,i))['current_state']
        tablelist.append(rowlist)
    return JsonResponse(tablelist, safe=False)



def get_console_output(request):
    appname=request.GET.get("appname")
    start_offset = request.GET.get("start_offset")
    env=request.GET.get("env")
    job_name=get_jenkins_job_name(env, appname)
    if env == "qa01" or env == "qa02":
        server = jenkins.Jenkins('http://jenkins.protest.xueba100.cc', username='haojie.liu',
                                password='01af9c58e0dad91abbfbece390fc620e')
        jenkins_last_buildnumber = server.get_job_info(job_name)['lastBuild']['number']
        text_str = '%s/job/%s/%s/logText/progressiveText?start=%s'
        auth = HTTPBasicAuth('haojie.liu', '01af9c58e0dad91abbfbece390fc620e')
        response = requests.get(text_str % ('http://jenkins.protest.xueba100.cc/',
                                            job_name, jenkins_last_buildnumber, start_offset), auth=auth)
    elif env == "plus":
        server = jenkins.Jenkins('http://jenkins.xueba100.cc/', username='haojie.liu',
                                 password='3fb7937bc6a3fa417ef4cb3dfaa560ae')
        jenkins_last_buildnumber = server.get_job_info(job_name)['lastBuild']['number']
        text_str = '%s/job/%s/%s/logText/progressiveText?start=%s'
        auth = HTTPBasicAuth('haojie.liu', '3fb7937bc6a3fa417ef4cb3dfaa560ae')
        response = requests.get(text_str % ('http://jenkins.xueba100.cc/',
                                            job_name, jenkins_last_buildnumber, start_offset), auth=auth)
    result = None
    if 'X-Text-Size' in response.headers:
        result = {'output': response.text, 'next_start_offset': response.headers['X-Text-Size']}
    else:
        result = {'output': response.text}
    if 'X-More-Data' in response.headers:
        result['more_data'] = True
        return JsonResponse(result)
    result['more_data'] = False
    return JsonResponse(result)






@csrf_exempt
def startbuild(request):
    branch_name=request.POST.get("branch_name")
    tag_version=request.POST.get("tag_version")
    env=request.POST.get("env")
    appname=request.POST.get("appname")
    username=request.user.username
    job_name=get_jenkins_job_name(env, appname)
    print(branch_name,tag_version,env,appname,username,job_name)
    if env == "qa01" or env == "qa02":
        server = jenkins.Jenkins('http://jenkins.protest.xueba100.cc', username='haojie.liu',
                             password='01af9c58e0dad91abbfbece390fc620e')
        if env == "qa02":
            job_name="qa02-aixue-open-pro/" + job_name
        tag_version="null"
        server.build_job(job_name,parameters={'branch_name':branch_name})
        
    elif env == "plus":
        server = jenkins.Jenkins('http://jenkins.xueba100.cc', username='haojie.liu',
                                 password='3fb7937bc6a3fa417ef4cb3dfaa560ae')
        print(job_name,tag_version)
        server.build_job(job_name, parameters={'branch_name': branch_name,'version':tag_version})
        
    building_number = server.get_job_info(job_name)['builds'][0]['number']
    building_number = building_number + 1
    
    while True:
            try:
                status=server.get_build_info(job_name,building_number)['building']
                result=server.get_build_info(job_name,building_number)['result']
            except Exception as e:
                time.sleep(3)
            else:
                if status:
                    time.sleep(3)
                else:
                    if result == "SUCCESS":
                        p = deploy_model.objects.create(appname=appname,deployer=username,
                            env=env,tag_version=tag_version,build_status=1,branch_name=branch_name)
                        print(p.id)
                        message = "构建成功"
                    else:
                        p = deploy_model.objects.create(appname=appname, deployer=username,
                            env=env, tag_version=tag_version, build_status=2,branch_name=branch_name)
                        print(p.id)
                        message="构建失败 请检查分支名、tag号是否正确 或联系运维"
                    break

    return JsonResponse({"message":message,"result":result,"tag_version":tag_version,"deployer":username})




@csrf_exempt
def startdeploy(request):
    username=request.user.username
    select = request.POST.get('select')
    select=json.loads(select)
    env=request.POST.get('env')
    appname=request.POST.get('appname')
    compose_name=get_compose_name(env,appname)
    tag_version=deploy_model.objects.filter(appname=appname)\
    .filter(env=env).order_by("-deploytime")[0].tag_version
    id=deploy_model.objects.filter(appname=appname)\
    .filter(env=env).order_by("-deploytime")[0].id
    deploy_status=deploy_model.objects.get(id=id).deploy_status
    if deploy_status != 0:
        message="deploy_again"
        return JsonResponse({"message":message})
    cert_access_url = {"qa01": "https://master2g8.cs-cn-hangzhou.aliyun.com:20064/projects/",
                       "qa02": "https://master3g5.cs-cn-hangzhou.aliyun.com:18651/projects/",
                       "plus": "https://master2g6.cs-cn-hangzhou.aliyun.com:16214/projects/"}
    aliyun_project_url = cert_access_url[env]
    ca_path = 'auto_deploy/certfile/certfile_' + env + '/ca.pem'
    cert_path = 'auto_deploy/certfile/certfile_' + env + '/cert.pem'
    key_path = 'auto_deploy/certfile/certfile_' + env + '/key.pem'
    res = requests.get(aliyun_project_url + appname, verify=ca_path, cert=(cert_path, key_path))
    template = yaml.load(json.loads(res.content)['template'])
    version = json.loads(res.content)['version']
    version=Decimal(version) + Decimal('0.01')
    fp=open('auto_deploy/env_list/' + env + '/' + appname)
    env=[]
    external_list=[]
    for line in fp.readlines():
        env.append(line.strip("'\"\n"))
    template[compose_name]['environment'] = env
    for line in select:
        external_list.append(line)
    template[compose_name]['external_links'] = external_list
    template[compose_name]['image']=re.sub(r':(.*)',':' + tag_version,template[compose_name]['image'])
    print(template[compose_name]['image'])
    template = yaml.dump(template, default_flow_style=False)
    d = {
        "template": template,
        "latest_image": True,
        "version": str(version),
        "environment": {
        }
     }
    action = 'update'
    res = requests.post(aliyun_project_url + appname + '/' + action, verify=ca_path, cert=(cert_path, key_path),
                        data=json.dumps(d))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if str(res.status_code) == "202":
        deploy_model.objects.filter(id=id).update(deploy_status=1)
        deploy_model.objects.filter(id=id).update(deploytime2=now)
        message = "yes"
    else:
        deploy_model.objects.filter(id=id).update(deploy_status=2)
        deploy_model.objects.filter(id=id).update(deploytime2=now)
        message = "no"
    return JsonResponse({"message":message,"tag_version":tag_version,"deployer":username})


def getcertfile(env,app):
    cert_access_url={"qa01":"https://master2g8.cs-cn-hangzhou.aliyun.com:20064/projects/",
                     "qa02":"https://master3g5.cs-cn-hangzhou.aliyun.com:18651/projects/",
                     "plus":"https://master2g6.cs-cn-hangzhou.aliyun.com:16214/projects/"}
    aliyun_project_url=cert_access_url[env]
    ca_path = 'auto_deploy/certfile/certfile_' + env + '/ca.pem'
    cert_path = 'auto_deploy/certfile/certfile_' + env + '/cert.pem'
    key_path = 'auto_deploy/certfile/certfile_' + env + '/key.pem'
    aliyun_appname = app
    res = requests.get(aliyun_project_url  + aliyun_appname,
                       verify=ca_path,
                       cert=(cert_path, key_path))
    return res.text



@csrf_exempt
def confile(request):
    env = request.POST.get('env')
    appname = request.POST.get('appname')
    f = request.FILES.get('file')
    if not os.path.exists('auto_deploy/env_list/' + env + '/'):
        os.makedirs('auto_deploy/env_list/' + env + '/')
    with open('auto_deploy/env_list/' + env + '/' + appname, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return JsonResponse({"message": 'ok'})


    
def list_external_link(request):
    appname = request.GET.get("appname")
    env = request.GET.get('env')
    compose_name = get_compose_name(env, appname)
    locallist = []
    pattern = re.compile(r'aliyun.routing.port_(.*)')
    pattern1 = re.compile(r'(.+).local')

    cert_access_url = {"qa01": "https://master2g8.cs-cn-hangzhou.aliyun.com:20064/projects/",
                       "qa02": "https://master3g5.cs-cn-hangzhou.aliyun.com:18651/projects/",
                       "plus": "https://master2g6.cs-cn-hangzhou.aliyun.com:16214/projects/"}
    aliyun_project_url = cert_access_url[env]
    ca_path = 'auto_deploy/certfile/certfile_' + env + '/ca.pem'
    cert_path = 'auto_deploy/certfile/certfile_' + env + '/cert.pem'
    key_path = 'auto_deploy/certfile/certfile_' + env + '/key.pem'
    cf = configparser.ConfigParser()
    cf.read("auto_deploy/conflist")
    o = cf.options(env)
    for app in o:
        aliyun_appname = app
        res = requests.get(aliyun_project_url + aliyun_appname, verify=ca_path, cert=(cert_path, key_path))
        result = yaml.load(json.loads(res.content)['template'])
        appname = list(result.keys())[0]
        for key in result[appname]['labels']:
            match = pattern.match(key)
            if match:
                resultlist = result[appname]['labels'][key].split(';')
                for i in resultlist:
                    if pattern1.match(i):
                        locallist.append(i)
    res = requests.get(aliyun_project_url + appname, verify=ca_path, cert=(cert_path, key_path))
    template = yaml.load(json.loads(res.content)['template'])
    external_link = template[compose_name]['external_links']
    locallist = list(set(locallist) - set(external_link))
    return JsonResponse({"locallist": locallist})



def history_list(request):
    appname=request.GET.get("appname")
    env=request.GET.get('env')
    historyList=deploy_model.objects.filter(appname=appname).filter(env=env).exclude(deploy_status=0).order_by("-deploytime2")[0:10].values_list(
    'appname', 'deployer', 'deploy_status', 'tag_version', 'deploytime2')
    resultlist=[]
    for i in historyList:
        print(i)
        if i[2] == 1:
            deploy_status="running"
        else:
            deploy_status="not running"
        deploytime=str(i[4]).split(".")[0]
        appname=i[0]
        deployer=i[1]
        tag_version=i[3]
        resultdict={"appname":appname,"deployer":deployer,"deploy_status":deploy_status,
                    "tag_version":tag_version,"deploytime":deploytime}
        resultdict=json.dumps(resultdict)
        resultlist.append(resultdict)
    return JsonResponse(resultlist,safe=False)


def get_jenkins_job_name(env,appname):
    cf = configparser.ConfigParser()
    cf.read("auto_deploy/conflist")
    s=cf.get(env,appname).split(":")[0]
    return s

def get_compose_name(env,appname):
    cf = configparser.ConfigParser()
    cf.read("auto_deploy/conflist")
    s = cf.get(env, appname).split(":")[1]
    return s

def getexistexternallist(request):
    appname = request.GET.get("appname")
    env = request.GET.get('env')
    compose_name=get_compose_name(env,appname)
    cert_access_url = {"qa01": "https://master2g8.cs-cn-hangzhou.aliyun.com:20064/projects/",
                       "qa02": "https://master3g5.cs-cn-hangzhou.aliyun.com:18651/projects/",
                       "plus": "https://master2g6.cs-cn-hangzhou.aliyun.com:16214/projects/"}
    aliyun_project_url = cert_access_url[env]
    ca_path = 'auto_deploy/certfile/certfile_' + env + '/ca.pem'
    cert_path = 'auto_deploy/certfile/certfile_' + env + '/cert.pem'
    key_path = 'auto_deploy/certfile/certfile_' + env + '/key.pem'
    res = requests.get(aliyun_project_url + appname, verify=ca_path, cert=(cert_path, key_path))
    template = yaml.load(json.loads(res.content)['template'])
    external_link=template[compose_name]['external_links']
    return JsonResponse({"external_list": external_link})

