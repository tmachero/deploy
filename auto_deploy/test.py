import os, sys
import requests
import json
import yaml
import re
import configparser

locallist = []
pattern = re.compile(r'aliyun.routing.port_(.*)')
pattern1 = re.compile(r'(.+).local')

env = "qa01"
app = "aixue-web-pro-mirror"
action = 'update'
cert_access_url = {"qa01": "https://master2g8.cs-cn-hangzhou.aliyun.com:20064/projects/",
                   "qa02": "https://master3g5.cs-cn-hangzhou.aliyun.com:18651/projects/",
                   "plus": "https://master2g6.cs-cn-hangzhou.aliyun.com:16214/projects/"}
aliyun_project_url = cert_access_url[env]
ca_path = 'certfile/certfile_' + env + '/ca.pem'
cert_path = 'certfile/certfile_' + env + '/cert.pem'
key_path = 'certfile/certfile_' + env + '/key.pem'
cf = configparser.ConfigParser()
cf.read("conflist")
o = cf.options("qa01")
for app in o:
    aliyun_appname = app
    res = requests.get(aliyun_project_url + aliyun_appname, verify=ca_path, cert=(cert_path, key_path))
    result = yaml.load(json.loads(res.content)['template'])
    appname=list(result.keys())[0]
    for key in result[appname]['labels']:
        match = pattern.match(key)
        if match:
            resultlist = result[appname]['labels'][key].split(';')
            for i in resultlist:
                if pattern1.match(i):
                    locallist.append(i)

