import re
test='registry.cn-hangzhou.aliyuncs.com/wenba/aixue-web-pro:v1.0.19'
tag_version='v1.0.18'

test=re.sub(r':(.*)',':' + tag_version,test)
print(test)