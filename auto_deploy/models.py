# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


#running_status:{0:ok,1:error} 容器在阿里云上状态
#build_status:{0:未构建,1:构建完成且成功,2:构建完成且失败}
#deploy_status:{0:未发布,1:发布完成且成功,2:发布完成且失败}


class deploy(models.Model):
    appname=models.CharField(max_length=50)
    deployer=models.CharField(max_length=20)
    env=models.CharField(max_length=20)
    tag_version=models.CharField(max_length=20,null=True)
    running_status=models.IntegerField(default=0)
    build_status=models.IntegerField(default=0)
    deploy_status=models.IntegerField(default=0)
    deploytime=models.DateTimeField(auto_now_add=True)
    deploytime2=models.DateTimeField(auto_now=True)
    branch_name=models.CharField(max_length=20,default='master')

    def __unicode__(self):
        return u'%s %s %s' % (self.appname, self.env,self.tag_version)
    class Meta:
        #unique_together = ("appname","env","tag_version")
        ordering = ['appname']
        db_table='deploy'
        