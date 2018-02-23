# -*- coding: utf-8 -*-
import jenkins
server = jenkins.Jenkins('http://jenkins.protest.xueba100.cc', username='haojie.liu', password='01af9c58e0dad91abbfbece390fc620e')
job_name="aixue-homework-pro-test"
jenkins_last_buildnumber=server.get_job_info(job_name)['lastBuild']['number']
jenkins_new_buildnumber=jenkins_last_buildnumber+1

param_dict={'branch_name':'release_ziyan2'}
server.build_job(job_name, parameters=param_dict)

#server.get_build_info(job_name,jenkins_new_buildnumber)['result']
