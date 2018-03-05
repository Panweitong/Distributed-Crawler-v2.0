import datetime
import json
import os
import tempfile
from urllib.parse import quote
import MySQLdb as mdb
import flask_restful
import math

import numpy as np
import requests
import xlwt
from PIL import Image
from flask import Blueprint, request, Response, jsonify, send_from_directory
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from flask_restful_swagger import swagger
from werkzeug.utils import secure_filename
from SpiderKeeper.app import db, api, agent, app
from SpiderKeeper.app.spider.InformationExtraction import getInformation
from SpiderKeeper.app.spider.TextAnalyzemain import TextAnalyze1, TextAnalyze2
from SpiderKeeper.app.spider.dataAnalyse import getCityNum, getAvg_Money, getComtype, getEduNum, getEdu_Money,getCity_Money
from SpiderKeeper.app.spider.jd_commentAnalyse import getDate, getRole, Comment_client, Comments_level, wordCloud1
from SpiderKeeper.app.spider.model import JobInstance, Project, JobExecution, SpiderInstance, JobRunType
from SpiderKeeper.app.spider.regres import countAbiity, wordCloud
from SpiderKeeper.app.spider.start import CRedis


api_spider_bp = Blueprint('spider', __name__)


'''
========= api =========
'''


class ProjectCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list projects',
        parameters=[])
    def get(self):
        return [project.to_dict() for project in Project.query.all()]

    @swagger.operation(
        summary='add project',
        parameters=[{
            "name": "project_name",
            "description": "project name",
            "required": True,
            "paramType": "form",
            "dataType": 'string'
        }])
    def post(self):
        project_name = request.form['project_name']
        project = Project()
        project.project_name = project_name
        db.session.add(project)
        db.session.commit()
        return project.to_dict()


class SpiderCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list spiders',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        project = Project.find_project_by_id(project_id)
        return [spider_instance.to_dict() for spider_instance in
                SpiderInstance.query.filter_by(project_id=project_id).all()]


class SpiderDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='spider detail',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_id",
            "description": "spider instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id, spider_id):
        spider_instance = SpiderInstance.query.filter_by(project_id=project_id, id=spider_id).first()
        return spider_instance.to_dict() if spider_instance else abort(404)

    @swagger.operation(
        summary='run spider',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_id",
            "description": "spider instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_arguments",
            "description": "spider arguments",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "tags",
            "description": "spider tags",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "spider desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }])
    def put(self, project_id, spider_id):
        spider_instance = SpiderInstance.query.filter_by(project_id=project_id, id=spider_id).first()
        if not spider_instance: abort(404)
        job_instance = JobInstance()
        job_instance.spider_name = spider_instance.spider_name
        job_instance.project_id = project_id
        job_instance.spider_arguments = request.form.get('spider_arguments')
        job_instance.desc = request.form.get('desc')
        job_instance.tags = request.form.get('tags')
        job_instance.run_type = JobRunType.ONETIME
        job_instance.priority = request.form.get('priority', 0)
        job_instance.enabled = -1
        db.session.add(job_instance)
        db.session.commit()
        agent.start_spider(job_instance)
        return True


JOB_INSTANCE_FIELDS = [column.name for column in JobInstance.__table__.columns]
JOB_INSTANCE_FIELDS.remove('id')
JOB_INSTANCE_FIELDS.remove('date_created')
JOB_INSTANCE_FIELDS.remove('date_modified')


class JobCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list job instance',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        return [job_instance.to_dict() for job_instance in
                JobInstance.query.filter_by(run_type="periodic", project_id=project_id).all()]

    @swagger.operation(
        summary='add job instance',
        notes="json keys: <br>" + "<br>".join(JOB_INSTANCE_FIELDS),
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_name",
            "description": "spider_name",
            "required": True,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "spider_arguments",
            "description": "spider_arguments,  split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "tags",
            "description": "tags , split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "run_type",
            "description": "onetime/periodic",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "cron_minutes",
            "description": "@see http://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_hour",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_week",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }])
    def post(self, project_id):
        post_data = request.form
        if post_data:
            job_instance = JobInstance()
            job_instance.spider_name = post_data['spider_name']
            job_instance.project_id = project_id
            job_instance.spider_arguments = post_data.get('spider_arguments')
            job_instance.desc = post_data.get('desc')
            job_instance.tags = post_data.get('tags')
            job_instance.run_type = post_data['run_type']
            job_instance.priority = post_data.get('priority', 0)
            if job_instance.run_type == "periodic":
                job_instance.cron_minutes = post_data.get('cron_minutes') or '0'
                job_instance.cron_hour = post_data.get('cron_hour') or '*'
                job_instance.cron_day_of_month = post_data.get('cron_day_of_month') or '*'
                job_instance.cron_day_of_week = post_data.get('cron_day_of_week') or '*'
                job_instance.cron_month = post_data.get('cron_month') or '*'
            db.session.add(job_instance)
            db.session.commit()
            return True


class JobDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='update job instance',
        notes="json keys: <br>" + "<br>".join(JOB_INSTANCE_FIELDS),
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "job_id",
            "description": "job instance id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }, {
            "name": "spider_name",
            "description": "spider_name",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "spider_arguments",
            "description": "spider_arguments,  split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "desc",
            "description": "desc",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "tags",
            "description": "tags , split by ','",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "run_type",
            "description": "onetime/periodic",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "priority",
            "description": "LOW: -1, NORMAL: 0, HIGH: 1, HIGHEST: 2",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "cron_minutes",
            "description": "@see http://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_hour",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_day_of_week",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "cron_month",
            "description": "",
            "required": False,
            "paramType": "form",
            "dataType": 'string'
        }, {
            "name": "enabled",
            "description": "-1 / 0, default: 0",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }, {
            "name": "status",
            "description": "if set to 'run' will run the job",
            "required": False,
            "paramType": "form",
            "dataType": 'int'
        }

        ])
    def put(self, project_id, job_id):
        post_data = request.form
        if post_data:
            job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_id).first()
            if not job_instance: abort(404)
            job_instance.spider_arguments = post_data.get('spider_arguments') or job_instance.spider_arguments
            job_instance.priority = post_data.get('priority') or job_instance.priority
            job_instance.enabled = post_data.get('enabled', 0)
            job_instance.cron_minutes = post_data.get('cron_minutes') or job_instance.cron_minutes
            job_instance.cron_hour = post_data.get('cron_hour') or job_instance.cron_hour
            job_instance.cron_day_of_month = post_data.get('cron_day_of_month') or job_instance.cron_day_of_month
            job_instance.cron_day_of_week = post_data.get('cron_day_of_week') or job_instance.cron_day_of_week
            job_instance.cron_month = post_data.get('cron_month') or job_instance.cron_month
            job_instance.desc = post_data.get('desc', 0) or job_instance.desc
            job_instance.tags = post_data.get('tags', 0) or job_instance.tags
            db.session.commit()
            if post_data.get('status') == 'run':
                agent.start_spider(job_instance)
            return True


class JobExecutionCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='list job execution status',
        parameters=[{
            "name": "project_id",
            "description": "project id",
            "required": True,
            "paramType": "path",
            "dataType": 'int'
        }])
    def get(self, project_id):
        return JobExecution.list_jobs(project_id)


class JobExecutionDetailCtrl(flask_restful.Resource):
    @swagger.operation(
        summary='stop job',
        notes='',
        parameters=[
            {
                "name": "project_id",
                "description": "project id",
                "required": True,
                "paramType": "path",
                "dataType": 'int'
            },
            {
                "name": "job_exec_id",
                "description": "job_execution_id",
                "required": True,
                "paramType": "path",
                "dataType": 'string'
            }
        ])
    def put(self, project_id, job_exec_id):
        job_execution = JobExecution.query.filter_by(project_id=project_id, id=job_exec_id).first()
        if job_execution:
            agent.cancel_spider(job_execution)
            return True


api.add_resource(ProjectCtrl, "/api/projects")
api.add_resource(SpiderCtrl, "/api/projects/<project_id>/spiders")
api.add_resource(SpiderDetailCtrl, "/api/projects/<project_id>/spiders/<spider_id>")
api.add_resource(JobCtrl, "/api/projects/<project_id>/jobs")
api.add_resource(JobDetailCtrl, "/api/projects/<project_id>/jobs/<job_id>")
api.add_resource(JobExecutionCtrl, "/api/projects/<project_id>/jobexecs")
api.add_resource(JobExecutionDetailCtrl, "/api/projects/<project_id>/jobexecs/<job_exec_id>")

'''
========= Router =========
'''


@app.before_request
def intercept_no_project():
    if request.path.find('/project//') > -1:
        flash("create project first")
        return redirect("/project/manage", code=302)


@app.context_processor
def inject_common():
    return dict(now=datetime.datetime.now(),
                servers=agent.servers)


@app.context_processor
def inject_project():
    project_context = {}
    project_context['project_list'] = Project.query.all()
    if project_context['project_list'] and (not session.get('project_id')):
        project = Project.query.first()
        session['project_id'] = project.id
    if session.get('project_id'):
        project_context['project'] = Project.find_project_by_id(session['project_id'])
        project_context['spider_list'] = [spider_instance.to_dict() for spider_instance in
                                          SpiderInstance.query.filter_by(project_id=session['project_id']).all()]
    else:
        project_context['project'] = {}
    return project_context


@app.context_processor
def utility_processor():
    def timedelta(end_time, start_time):
        '''

        :param end_time:
        :param start_time:
        :param unit: s m h
        :return:
        '''
        if not end_time or not start_time:
            return ''
        if type(end_time) == str:
            end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        if type(start_time) == str:
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        total_seconds = (end_time - start_time).total_seconds()
        return readable_time(total_seconds)

    def readable_time(total_seconds):
        if not total_seconds:
            return '-'
        if total_seconds / 60 == 0:
            return '%s s' % total_seconds
        if total_seconds / 3600 == 0:
            return '%s m' % int(total_seconds / 60)
        return '%s h %s m' % (int(total_seconds / 3600), int((total_seconds % 3600) / 60))

    return dict(timedelta=timedelta, readable_time=readable_time)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/project")
def manage():
    project = Project.query.first()
    if project:
        return redirect("/project/%s/job/dashboard" % project.id, code=302)
    return redirect("/project/manage", code=302)


@app.route("/dataAnalyse")
def data_Analyse():
    return render_template("city_distribute.html")


@app.route("/<project_id>/job/add", methods=['post'])
def add(project_id):
    con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    cur = con.cursor()
    project = Project.find_project_by_id(project_id)
    job_instance = JobInstance()
    job_instance.spider_name = request.values.get('spider_name')
    job_instance.project_id = project_id
    job_instance.spider_arguments = request.values.get('spider_arguments')
    job_instance.priority = request.values.get('priority')
    job_instance.run_type = request.values.get('run_type')
    spider_url = request.values.get('spider_url')
    spider_models = request.values.get('spider_models')
    key = request.values.get('key')
    area = request.values.get('area')
    key1 = job_instance.spider_name + ":items"
    key2 = job_instance.spider_name + ":requests"
    key3 = job_instance.spider_name + ":dupefilter"
    r = CRedis()
    r.remove(key1)
    r.remove(key2)
    r.remove(key3)
    sql = "TRUNCATE TABLE job_cache"
    cur.execute(sql)
    sql = "delete from state where id = 0"
    cur.execute(sql)
    con.commit()
    cur.close()
    con.close()
    if area == '0':
        key = quote(str(key))
        spider_url = "https://www.liepin.com/zhaopin/?headckid=1&key=" + key
        r = CRedis()
        r.lpush('liepin:start_urls', spider_url)

    else:
        key = quote(str(key))
        spider_url = "https://www.liepin.com/zhaopin/?headckid=1&dqs=" + area + "&key=" + key
        r = CRedis()
        r.lpush('liepin:start_urls', spider_url)


    if job_instance.run_type == JobRunType.ONETIME:
        job_instance.enabled = -1
        db.session.add(job_instance)
        db.session.commit()
        agent.start_spider(job_instance)
    return redirect(request.referrer, code=302)


@app.route('/buy/date', methods=['POST'])
def buy_date():
    name = request.values.get("id")
    print(name)
    data = getDate(name)
    return data


@app.route('/buy/role', methods=['POST'])
def buy_role():
    name = request.values.get("id")
    data = getRole(name)
    return data


@app.route('/buy/client', methods=['POST'])
def buy_client():
    name = request.values.get("id")
    data = Comment_client(name)
    return data


@app.route('/buy/level', methods=['POST'])
def buy_level():
    name = request.values.get("id")
    data = Comments_level(name)
    return data


@app.route('/city/distribute', methods=['POST'])
def city_distribute():
    data = getCityNum()
    return data


@app.route('/city/money', methods=['POST'])
def city_money():
    data = getAvg_Money()
    return data


@app.route('/company/type', methods=['POST'])
def company_type():
    data = getComtype()
    return data


@app.route('/education/type', methods=['POST'])
def education_type():
    data = getEduNum()
    return data


@app.route('/education/money', methods=['POST'])
def education_money():
    data = getEdu_Money()
    return data


@app.route('/avg/money', methods=['POST'])
def avg_money():
    data = getCity_Money()
    return data


@app.route('/job/ability', methods=['POST'])
def job_ability():
    data1, data2 = countAbiity()
    # data1 = json.dumps(data1)
    # data2 = json.dumps(data2)
    result = {"data1": data1, "data2": data2}
    return json.dumps(result, ensure_ascii=False)


@app.route('/word/cloud', methods=['POST'])
def word_cloud():
    wordCloud()
    return '成功'


@app.route("/image/dg")
def image():
    image = open(r"C:\Users\Administrator\Desktop\SpiderKeeper-master\SpiderKeeper-master\SpiderKeeper\app\static\images\cloud.png",'rb')
    resp = Response(image, mimetype="image/jpeg")
    return resp


@app.route("/image/fg")
def image_fg():
    image = open(r"C:\Users\Administrator\Desktop\SpiderKeeper-master\SpiderKeeper-master\SpiderKeeper\app\static\images\cloud_comm.png",'rb')
    resp = Response(image, mimetype="image/jpeg")
    return resp


# @app.route('/word/cloud/comm', methods=['POST'])
# def word_cloud_comm():
#     name = request.values.get("id")
#     print(name)
#     wordCloud1(name)
#     return "成功"


@app.route('/clear', methods=['POST'])
def clear_jd_spider():
    r = CRedis()
    r.clear()
    return "你已经清空所有队列！"


@app.route('/date', methods=['POST'])
def date():
    url = request.values.get("url")
    name = requests.get("http://123.207.12.105:9100/?p="+url).content
    name = "网站最后更新时间为: " + name.decode()
    return name


@app.route('/close', methods=['POST'])
def CloseJdSpider():
    spider_name = request.values.get("spider_name")
    key1 = spider_name + ":items"
    key2 = spider_name + ":requests"
    key3 = spider_name + ":dupefilter"
    r = CRedis()
    r.remove(key1)
    r.remove(key2)
    r.remove(key3)
    return "你已经删除该队列！"


@app.route('/TextAnalyze/', methods=['POST'])
def getTextAnalyze():
    text = request.values.get('text')
    result1 = TextAnalyze1(text)
    # print(result1)
    result2 = TextAnalyze2(text)
    # print(result2)
    result = {'result1': ('').join(result1), 'result2': result2}
    return json.dumps(result)


@app.route('/Content/', methods=['POST'])
def Content():
    url = request.values.get('text')
    content = getInformation(url)
    return content


@app.route('/analysis/')
def analysis():
    return render_template("analysis.html")


'''
========= jd =========
'''


@app.route('/jd/comment', methods=['GET'])
def jd_comment():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        name = request.args.get('id')
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 5
        sql = "SELECT * FROM jd_comment WHERE good_ID=" + name + " LIMIT " + str(a) + ", 5"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
                {'username': infor[1], 'content': infor[4], 'date': infor[7], 'score': infor[9], 'type': infor[13], 'productSize': infor[14],
                 'leverName': infor[15], 'source': infor[19]})
        count_sql = "SELECT count(*) FROM jd_comment WHERE good_ID=" + name
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        #   count1 = json.dumps(count_sql)
        #   count2=json.loads(count)
        #   c=int(count1)
        cur.close()
        con.close()
        # print(count)
        if count % 5 == 0:
            num_pages = int(count / 5)  # 总共的页码
        else:
            num_pages = math.ceil(count / 5 )  # 不解释
        last_page = int(num_pages) - 1 # 最后页
        int_curr_page = int(curr_page)+1  # 获取url中的页码
        previous_page_number = int_curr_page - 1  # 当前页的前一页
        nex_page_number = int_curr_page + 1  # 当前页的后一页
        return json.dumps({
            'result': results, 'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1
        })


@app.route('/jd/comment/count', methods=['GET'])
def jd_comment_count():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        name = request.args.get('id')
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 5
        sql = "SELECT * FROM jd_comment WHERE good_ID=" + name + " LIMIT " + str(a) + ", 5"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
            results.append(
                {'username': infor[1], 'content': infor[4], 'date': infor[7], 'score': infor[9], 'type': infor[13], 'productSize': infor[14],
                 'leverName': infor[15], 'source': infor[19]})
        count_sql = "SELECT count(*) FROM jd_comment WHERE good_ID=" + name
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        cur.close()
        con.close()
        if count % 5 == 0:
            num_pages = int(count / 5)  # 总共的页码
        else:
            num_pages = math.ceil(count / 5 )  # 不解释
        count = str(count)
        num_pages = str(num_pages)
        return json.dumps({'count': count, 'numPages': num_pages, "result": results})


@app.route('/jd/exportCommentData', methods=['POST'])
def export_jd_comment_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM jd_comment'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xlsx'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                if len(results[row-1][col])>65500:
                    sheet.write(row,col,"")
                else:
                    sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/jd/exportData', methods=['POST'])
def export_jd_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM jd_goods'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xls'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/jd/exportCacheData', methods=['POST'])
def export_jd_cache_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM jd_goods_cache'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xls'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/jd/count', methods=['GET'])
def jd_count():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 10
        sql = "SELECT * FROM jd_goods_cache LIMIT " + str(a) + ", 10"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
                {'id': infor[0], 'title': infor[1], 'price': infor[3], 'evaluate': infor[6], 'store': infor[4], 'score1': infor[8],
                 'score2': infor[9], 'score3': infor[10], 'score4': infor[11], 'score5': infor[12], 'url': infor[2]})
        count_sql = "SELECT count(*) FROM jd_goods_cache"
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        cur.close()
        con.close()
        if count % 10 == 0:
            num_pages = int(count / 10)  # 总共的页码
        else:
            num_pages = math.ceil(count / 10 )  # 不解释
        count = str(count)
        num_pages = str(num_pages)
        return json.dumps({'count': count, 'numPages': num_pages, "result": results})


@app.route('/jd/index', methods=['GET'])
def jd_index():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        #    curr_page=request.GET.get("page","")
        #    curr_page=request.GET["page"]
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 10
        sql = "SELECT * FROM jd_goods_cache LIMIT " + str(a) + ", 10"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
                {'id': infor[0], 'title': infor[1], 'price': infor[3], 'evaluate': infor[6], 'store': infor[4], 'score1': infor[8],
                 'score2': infor[9], 'score3': infor[10], 'score4': infor[11], 'score5': infor[12], 'url': infor[2]})
        count_sql = "SELECT count(*) FROM jd_goods_cache"
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        #   count1 = json.dumps(count_sql)
        #   count2=json.loads(count)
        #   c=int(count1)
        cur.close()
        con.close()
        # print(count)
        if count % 10 == 0:
            num_pages = int(count / 10)  # 总共的页码
        else:
            num_pages = math.ceil(count / 10 )  # 不解释
        last_page = int(num_pages) - 1 # 最后页
        int_curr_page = int(curr_page)+1  # 获取url中的页码
        previous_page_number = int_curr_page - 1  # 当前页的前一页
        nex_page_number = int_curr_page + 1  # 当前页的后一页
        result=[]
        result.append(
            {'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1, 'previous_page_number': previous_page_number, 'nex_page_number': nex_page_number, 'last_page': last_page})
        return render_template("jd/jd_index.html", results=results, result=result)


@app.route('/jd/info',methods=['GET'])
def info():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        #    curr_page=request.GET.get("page","")
        #    curr_page=request.GET["page"]
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 20
        sql = "SELECT * FROM jd_goods LIMIT " + str(a) + ", 20"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
               {'id': infor[0], 'title': infor[1], 'price': infor[3], 'evaluate': infor[6], 'store': infor[4], 'score1': infor[8],
                'score2': infor[9], 'score3': infor[10], 'score4': infor[11], 'score5': infor[12], 'url': infor[2]})
        count_sql = "SELECT count(*) FROM jd_goods"
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        #   count1 = json.dumps(count_sql)
        #   count2=json.loads(count)
        #   c=int(count1)
        cur.close()
        con.close()
        # print(count)
        if count % 20 == 0:
            num_pages = int(count / 20)  # 总共的页码
        else:
            num_pages = math.ceil(count / 20 )  # 不解释
        last_page = int(num_pages)-1 # 最后页
        int_curr_page = int(curr_page)+1  # 获取url中的页码
        previous_page_number = int_curr_page - 1  # 当前页的前一页
        nex_page_number = int_curr_page + 1  # 当前页的后一页
        result=[]
        result.append(
            {'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1, 'previous_page_number': previous_page_number, 'nex_page_number': nex_page_number, 'last_page': last_page})
        return render_template('jd/info.html', results=results, result=result)


'''
========= recruit =========
'''


@app.route('/count', methods=['POST'])
def count():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT state FROM state WHERE id=0'
        cur.execute(sql)
        infor = None
        for ids in cur.fetchall():
            if ids[0]:
               infor = ids[0]
            else:
               infor = {"downloader_response_status_count_200": 0, "start_time": 0, "msg": "正在采集", "request_depth_max": 0, "isStop": 0, "log_count_DEBUG": 0, "log_count_INFO": 0, "log_count_WARNING": 0, "downloader_request_method_count_GET": 0, "scheduler_enqueued_redis": 0, "downloader_request_count": 0, "response_received_count": 0, "scheduler_dequeued_redis": 0, "downloader_response_count": 0, "downloader_response_bytes": 0, "downloader_request_bytes": 0, "item_scraped_count": 0}
        print(infor)
        return infor


@app.route('/recruit/exportData', methods=['POST'])
def export_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM job'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xls'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/recruit/exportCacheData', methods=['POST'])
def export_cache_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM job_cache'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xls'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/recruit/count', methods=['GET'])
def recruit_count():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 10
        sql = "SELECT * FROM job_cache LIMIT " + str(a) + ", 10"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
                {'comName': infor[11], 'name': infor[1], 'money': infor[3], 'area': infor[4], 'remark': infor[9],
                 'experience': infor[6], 'age': infor[8]})
        count_sql = "SELECT count(*) FROM job_cache"
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        cur.close()
        con.close()
        if count % 10 == 0:
            num_pages = int(count / 10)  # 总共的页码
        else:
            num_pages = math.ceil(count / 10 )  # 不解释
        count = str(count)
        num_pages = str(num_pages)
        return json.dumps({'count': count, 'numPages': num_pages, "result": results})


@app.route('/recruit/index', methods=['GET'])
def recruit_index():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        #    curr_page=request.GET.get("page","")
        #    curr_page=request.GET["page"]
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 10
        sql = "SELECT * FROM job_cache LIMIT " + str(a) + ", 10"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
                {'comName': infor[11], 'name': infor[1], 'money': infor[3], 'area': infor[4], 'remark': infor[9],
                 'experience': infor[6], 'age': infor[8]})
        count_sql = "SELECT count(*) FROM job_cache"
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        #   count1 = json.dumps(count_sql)
        #   count2=json.loads(count)
        #   c=int(count1)
        cur.close()
        con.close()
        # print(count)
        if count % 10 == 0:
            num_pages = int(count / 10)  # 总共的页码
        else:
            num_pages = math.ceil(count / 10 )  # 不解释
        last_page = int(num_pages)-1 # 最后页
        int_curr_page = int(curr_page)+1  # 获取url中的页码
        previous_page_number = int_curr_page - 1  # 当前页的前一页
        nex_page_number = int_curr_page + 1  # 当前页的后一页
        result=[]
        result.append(
            {'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1, 'previous_page_number': previous_page_number, 'nex_page_number': nex_page_number, 'last_page': last_page})
        return render_template("recruit/recruit_index.html", results=results, result=result)


@app.route('/recruit/recruit',methods=['GET'])
def recruit():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        #    curr_page=request.GET.get("page","")
        #    curr_page=request.GET["page"]
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 20
        sql = "SELECT * FROM job LIMIT " + str(a) + ", 20"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
                {'comName': infor[11], 'name': infor[1], 'money': infor[3], 'area': infor[4], 'remark': infor[9],
                 'experience': infor[6], 'age': infor[8]})
        count_sql = "SELECT count(*) FROM job"
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        #   count1 = json.dumps(count_sql)
        #   count2=json.loads(count)
        #   c=int(count1)
        cur.close()
        con.close()
        # print(count)
        if count % 20 == 0:
            num_pages = int(count / 20)  # 总共的页码
        else:
            num_pages = math.ceil(count / 20 )  # 不解释
        last_page = int(num_pages)-1 # 最后页
        int_curr_page = int(curr_page)+1  # 获取url中的页码
        previous_page_number = int_curr_page - 1  # 当前页的前一页
        nex_page_number = int_curr_page + 1  # 当前页的后一页
        result=[]
        result.append(
            {'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1, 'previous_page_number': previous_page_number, 'nex_page_number': nex_page_number, 'last_page': last_page})
        return render_template('recruit/recruit.html', results=results, result=result)


'''
========= newsBlog =========
'''


@app.route('/newsBlog/exportData', methods=['POST'])
def export_newsBlog_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM news_content'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xls'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/newsBlog/exportCacheData', methods=['POST'])
def export_newsBlog_cache_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM news_content_cache'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xls'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/newsBlog/count', methods=['GET'])
def newsBlog_count():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 10
        sql = "SELECT * FROM news_content_cache LIMIT " + str(a) + ", 10"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
                {'title': infor[1], 'source': infor[2], 'url': infor[3], 'content': infor[4]})
        count_sql = "SELECT count(*) FROM news_content_cache"
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        cur.close()
        con.close()
        if count % 10 == 0:
            num_pages = int(count / 10)  # 总共的页码
        else:
            num_pages = math.ceil(count / 10 )  # 不解释
        count = str(count)
        num_pages = str(num_pages)
        return json.dumps({'count': count, 'numPages': num_pages, "result": results})


@app.route('/newsBlog/index', methods=['GET'])
def newsBlog_index():
    con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    cur = con.cursor()
    #    curr_page=request.GET.get("page","")
    #    curr_page=request.GET["page"]
    curr_page = int(request.args.get("page"))-1
    a = int(curr_page) * 10
    sql = "SELECT * FROM news_content_cache LIMIT " + str(a) + ", 10"
    cur.execute(sql)
    infors = cur.fetchall()
    results = []
    for infor in infors:
        results.append(
            {'title': infor[1], 'source': infor[2], 'url': infor[3], 'content': infor[4]})
    count_sql = "SELECT count(*) FROM news_content_cache"
    cur.execute(count_sql)
    count_sql = cur.fetchall()
    count = count_sql[0][0]
    #   count1 = json.dumps(count_sql)
    #   count2=json.loads(count)
    #   c=int(count1)
    cur.close()
    con.close()
    # print(count)
    if count % 10 == 0:
        num_pages = int(count / 10)  # 总共的页码
    else:
        num_pages = math.ceil(count / 10)  # 不解释
    last_page = int(num_pages) - 1  # 最后页
    int_curr_page = int(curr_page)  # 获取url中的页码
    if int_curr_page == 0:  # 判断是否有前一页
        has_previous = False
    else:
        has_previous = True
    if int_curr_page == int(num_pages) - 1:  # 判断是否有下一页
        has_next = False
    else:
        has_next = True
    previous_page_number = int_curr_page - 1  # 当前页的前一页
    nex_page_number = int_curr_page + 1  # 当前页的后一页
    result = []
    result.append(
        {'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1, 'previous_page_number': previous_page_number,
         'nex_page_number': nex_page_number, 'last_page': last_page, 'has_previous': has_previous,
         'has_next': has_next})
    return render_template("newsBlog/news_index.html", results=results, result=result)


@app.route('/newsBlog/blog',methods=['GET'])
def newsBlog_blog():
    con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    cur = con.cursor()
    #    curr_page=request.GET.get("page","")
    #    curr_page=request.GET["page"]
    curr_page = int(request.args.get("page"))-1
    a = int(curr_page) * 20
    sql = "SELECT * FROM news_content LIMIT " + str(a) + ", 20"
    cur.execute(sql)
    infors = cur.fetchall()
    results = []
    for infor in infors:
        results.append(
            {'title': infor[1], 'source': infor[2], 'url': infor[3], 'content': infor[4]})
    count_sql = "SELECT count(*) FROM news_content"
    cur.execute(count_sql)
    count_sql = cur.fetchall()
    count = count_sql[0][0]
    #   count1 = json.dumps(count_sql)
    #   count2=json.loads(count)
    #   c=int(count1)
    cur.close()
    con.close()
    # print(count)
    if count % 20 == 0:
        num_pages = int(count / 20)  # 总共的页码
    else:
        num_pages = math.ceil(count / 20)  # 不解释
    last_page = int(num_pages) - 1  # 最后页
    int_curr_page = int(curr_page)  # 获取url中的页码
    if int_curr_page == 0:  # 判断是否有前一页
        has_previous = False
    else:
        has_previous = True
    if int_curr_page == int(num_pages) - 1:  # 判断是否有下一页
        has_next = False
    else:
        has_next = True
    previous_page_number = int_curr_page - 1  # 当前页的前一页
    nex_page_number = int_curr_page + 1  # 当前页的后一页
    result = []
    result.append(
        {'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1, 'previous_page_number': previous_page_number,
         'nex_page_number': nex_page_number, 'last_page': last_page, 'has_previous': has_previous,
         'has_next': has_next})
    return render_template('newsBlog/blog.html', results=results, result=result)


'''
========= google=========
'''


@app.route('/google/news/count', methods=['POST'])
def google_news_count():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT state FROM state WHERE id=1'
        cur.execute(sql)
        infor = {'downloader_response_status_count_200': 0, 'start_time': 0, 'msg': '正在采集', 'request_depth_max': 0, 'isStop': 2, 'log_count_DEBUG': 0, 'log_count_INFO': 0, 'log_count_WARNING': 0, 'downloader_request_method_count_GET': 0, 'scheduler_enqueued_redis': 0, 'downloader_request_count': 0, 'response_received_count': 0, 'scheduler_dequeued_redis': 0, 'downloader_response_count': 0, 'downloader_response_bytes': 0, 'downloader_request_bytes': 0, 'item_scraped_count': 0}
        infor = json.dumps(infor, ensure_ascii=False)
        for ids in cur.fetchall():
            infor = ids[0]
        print(infor)
        return infor


@app.route('/google/news/search', methods=['POST'])
def google_news_search():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        name = request.values.get("id")
        sql = 'SELECT * FROM google_news_cache WHERE id=' + name
        cur.execute(sql)
        infors = cur.fetchall()
        results = ""
        for infor in infors:
            results = {'title': infor[1], 'source': infor[2], 'url': infor[3], 'content': infor[4], "date": infor[5]}
        return json.dumps(results,ensure_ascii=False)


@app.route('/google/search', methods=['POST'])
def google_search():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        name = request.values.get("id")
        sql = 'SELECT * FROM google_news WHERE id=' + name
        cur.execute(sql)
        infors = cur.fetchall()
        results = ""
        for infor in infors:
            results = {'title': infor[1], 'source': infor[2], 'url': infor[3],  'content': infor[4], "date": infor[5]}
        return json.dumps(results,ensure_ascii=False)


@app.route('/google/exportData', methods=['POST'])
def export_google_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM google_news'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xls'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/google/exportCacheData', methods=['POST'])
def export_google_cache_data():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        sql = 'SELECT * FROM google_news_cache'
        sheet_name = 'job'
        out_path = r'C:/Users/Administrator/Desktop/SpiderKeeper-master/SpiderKeeper-master/SpiderKeeper/app/static/download/'+datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xls'
        count = cur.execute(sql)
        fields = cur.description
        cur.scroll(0,mode='absolute')
        results = cur.fetchall()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name,cell_overwrite_ok=True)
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
        workbook.save(out_path)
        filename = out_path.split("download/")[1]
        return json.dumps({'state': '导出成功', 'filename': filename},ensure_ascii=False)


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename, as_attachment=True)


@app.route('/google/count', methods=['GET'])
def google_count():
        con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
        cur = con.cursor()
        curr_page = int(request.args.get("page"))-1
        a = int(curr_page) * 10
        sql = "SELECT * FROM google_news_cache LIMIT " + str(a) + ", 10"
        cur.execute(sql)
        infors = cur.fetchall()
        results = []
        for infor in infors:
             results.append(
                {'id': infor[0], 'title': infor[1], 'source': infor[2], 'url': infor[3], 'content': infor[4]})
        count_sql = "SELECT count(*) FROM google_news_cache"
        cur.execute(count_sql)
        count_sql = cur.fetchall()
        count = count_sql[0][0]
        cur.close()
        con.close()
        if count % 10 == 0:
            num_pages = int(count / 10)  # 总共的页码
        else:
            num_pages = math.ceil(count / 10 )  # 不解释
        count = str(count)
        num_pages = str(num_pages)
        return json.dumps({'count': count, 'numPages': num_pages, "result": results})


@app.route('/google/index', methods=['GET'])
def google_index():
    con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    cur = con.cursor()
    #    curr_page=request.GET.get("page","")
    #    curr_page=request.GET["page"]
    curr_page = int(request.args.get("page"))-1
    a = int(curr_page) * 10
    sql = "SELECT * FROM google_news_cache LIMIT " + str(a) + ", 10"
    cur.execute(sql)
    infors = cur.fetchall()
    results = []
    for infor in infors:
        results.append(
            {'id': infor[0], 'title': infor[1], 'source': infor[2], 'url': infor[3], 'content': infor[4]})
    count_sql = "SELECT count(*) FROM google_news_cache"
    cur.execute(count_sql)
    count_sql = cur.fetchall()
    count = count_sql[0][0]
    #   count1 = json.dumps(count_sql)
    #   count2=json.loads(count)
    #   c=int(count1)
    cur.close()
    con.close()
    # print(count)
    if count % 10 == 0:
        num_pages = int(count / 10)  # 总共的页码
    else:
        num_pages = math.ceil(count / 10)  # 不解释
    last_page = int(num_pages) - 1  # 最后页
    int_curr_page = int(curr_page)  # 获取url中的页码
    if int_curr_page == 0:  # 判断是否有前一页
        has_previous = False
    else:
        has_previous = True
    if int_curr_page == int(num_pages) - 1:  # 判断是否有下一页
        has_next = False
    else:
        has_next = True
    previous_page_number = int_curr_page - 1  # 当前页的前一页
    nex_page_number = int_curr_page + 1  # 当前页的后一页
    result = []
    result.append(
        {'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1, 'previous_page_number': previous_page_number,
         'nex_page_number': nex_page_number, 'last_page': last_page, 'has_previous': has_previous,
         'has_next': has_next})
    return render_template("google/google_index.html", results=results, result=result)


@app.route('/google/google',methods=['GET'])
def google_google():
    con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    cur = con.cursor()
    #    curr_page=request.GET.get("page","")
    #    curr_page=request.GET["page"]
    curr_page = int(request.args.get("page"))-1
    a = int(curr_page) * 20
    sql = "SELECT * FROM google_news LIMIT " + str(a) + ", 20"
    cur.execute(sql)
    infors = cur.fetchall()
    results = []
    for infor in infors:
        results.append(
            {'id': infor[0], 'title': infor[1], 'source': infor[2], 'url': infor[3], 'content': infor[4]})
    count_sql = "SELECT count(*) FROM google_news"
    cur.execute(count_sql)
    count_sql = cur.fetchall()
    count = count_sql[0][0]
    #   count1 = json.dumps(count_sql)
    #   count2=json.loads(count)
    #   c=int(count1)
    cur.close()
    con.close()
    # print(count)
    if count % 20 == 0:
        num_pages = int(count / 20)  # 总共的页码
    else:
        num_pages = math.ceil(count / 20)  # 不解释
    last_page = int(num_pages) - 1  # 最后页
    int_curr_page = int(curr_page)  # 获取url中的页码
    if int_curr_page == 0:  # 判断是否有前一页
        has_previous = False
    else:
        has_previous = True
    if int_curr_page == int(num_pages) - 1:  # 判断是否有下一页
        has_next = False
    else:
        has_next = True
    previous_page_number = int_curr_page - 1  # 当前页的前一页
    nex_page_number = int_curr_page + 1  # 当前页的后一页
    result = []
    result.append(
        {'count': count, 'num_pages': num_pages, 'curr_page': curr_page+1, 'previous_page_number': previous_page_number,
         'nex_page_number': nex_page_number, 'last_page': last_page, 'has_previous': has_previous,
         'has_next': has_next})
    return render_template('google/google.html', results=results, result=result)


@app.route("/project/<project_id>")
def project_index(project_id):
    session['project_id'] = project_id
    return redirect("/project/%s/job/dashboard" % project_id, code=302)


@app.route("/project/create", methods=['post'])
def project_create():
    project_name = request.form['project_name']
    project = Project()
    project.project_name = project_name
    db.session.add(project)
    db.session.commit()
    return redirect("/project/%s/spider/deploy" % project.id, code=302)


@app.route("/project/<project_id>/delete")
def project_delete(project_id):
    project = Project.find_project_by_id(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect("/project/manage", code=302)


@app.route("/project/manage")
def project_manage():
    return render_template("project_manage.html")


@app.route("/project/<project_id>/job/dashboard")
def job_dashboard(project_id):
    return render_template("job_dashboard.html", job_status=JobExecution.list_jobs(project_id))


@app.route("/project/<project_id>/job/periodic")
def job_periodic(project_id):
    project = Project.find_project_by_id(project_id)
    job_instance_list = [job_instance.to_dict() for job_instance in
                         JobInstance.query.filter_by(run_type="periodic", project_id=project_id).all()]
    return render_template("job_periodic.html",
                           job_instance_list=job_instance_list)


@app.route("/project/<project_id>/job/add", methods=['post'])
def job_add(project_id):
    con = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    cur = con.cursor()
    project = Project.find_project_by_id(project_id)
    job_instance = JobInstance()
    job_instance.spider_name = request.form['spider_name']
    job_instance.project_id = project_id
    job_instance.spider_arguments = request.form['spider_arguments']
    job_instance.priority = request.form.get('priority', 0)
    job_instance.run_type = request.form['run_type']
    spider_url = request.form['spider_url']
    spider_models = request.form['spider_models']
    key = request.form['key']
    area = request.form.get('area', 0)
    key1 = job_instance.spider_name + ":items"
    key2 = job_instance.spider_name + ":requests"
    key3 = job_instance.spider_name + ":dupefilter"
    r = CRedis()
    r.remove(key1)
    r.remove(key2)
    r.remove(key3)

    if job_instance.spider_name == "news":
        allowed_domains=spider_url.split('/')[2]
        a = "allowed_domains="+allowed_domains
        a = a+","+"model="+spider_models
        job_instance.spider_arguments = a
        sql = "TRUNCATE TABLE news_content_cache"
        cur.execute(sql)
        cur.close()
        con.close()
        r = CRedis()
        r.lpush(allowed_domains+':start_urls', spider_url)

    elif job_instance.spider_name =='jd':
        sql = "TRUNCATE TABLE jd_goods_cache"
        cur.execute(sql)
        cur.close()
        con.close()
        r = CRedis()
        if key != "":
            key = quote(str(key))
            spider_url = "http://search.jd.com/Search?&enc=utf-8&keyword=" + key
            r.lpush('jd:start_urls', spider_url)
        else:
            for i in str(spider_models).split(";"):
                key = i
                key = quote(str(key))
                spider_url = "http://search.jd.com/Search?&enc=utf-8&keyword=" + key
                r.lpush('jd:start_urls', spider_url)

    elif job_instance.spider_name =='googlenews':
        sql = "TRUNCATE TABLE google_news_cache"
        cur.execute(sql)
        sql = "delete from state where id = 1"
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()
        key = quote(str(key))
        spider_url = "https://guge5.firstguo.com/search?num=100&tbm=nws&btnK=Google+%E6%90%9C%E7%B4%A2&q=" + key
        r = CRedis()
        r.lpush('googlenews:start_urls', spider_url)

    elif job_instance.spider_name =='liepin':
        sql = "TRUNCATE TABLE job_cache"
        cur.execute(sql)
        sql = "delete from state where id = 0"
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()
        if area == '0':
            key = quote(str(key))
            spider_url = "https://www.liepin.com/zhaopin/?headckid=1&key=" + key
            r = CRedis()
            r.lpush('liepin:start_urls', spider_url)

        else:
            key = quote(str(key))
            spider_url = "https://www.liepin.com/zhaopin/?headckid=1&dqs=" + area + "&key=" + key
            r = CRedis()
            r.lpush('liepin:start_urls', spider_url)

    if job_instance.run_type == JobRunType.ONETIME:
        job_instance.enabled = -1
        db.session.add(job_instance)
        db.session.commit()
        agent.start_spider(job_instance)
    if job_instance.run_type == JobRunType.PERIODIC:
        job_instance.cron_minutes = request.form.get('cron_minutes') or '0'
        job_instance.cron_hour = request.form.get('cron_hour') or '*'
        job_instance.cron_day_of_month = request.form.get('cron_day_of_month') or '*'
        job_instance.cron_day_of_week = request.form.get('cron_day_of_week') or '*'
        job_instance.cron_month = request.form.get('cron_month') or '*'
        db.session.add(job_instance)
        db.session.commit()
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/jobexecs/<job_exec_id>/stop")
def job_stop(project_id, job_exec_id):
    job_execution = JobExecution.query.filter_by(project_id=project_id, id=job_exec_id).first()
    agent.cancel_spider(job_execution)
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/jobexecs/<job_exec_id>/log")
def job_log(project_id, job_exec_id):
    job_execution = JobExecution.query.filter_by(project_id=project_id, id=job_exec_id).first()
    raw = requests.get(agent.log_url(job_execution)).text or ""
    return render_template("job_log.html", log_lines=raw.split('\n'))


@app.route("/project/<project_id>/job/<job_instance_id>/run")
def job_run(project_id, job_instance_id):
    job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_instance_id).first()
    agent.start_spider(job_instance)
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/job/<job_instance_id>/remove")
def job_remove(project_id, job_instance_id):
    job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_instance_id).first()
    db.session.delete(job_instance)
    db.session.commit()
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/job/<job_instance_id>/switch")
def job_switch(project_id, job_instance_id):
    job_instance = JobInstance.query.filter_by(project_id=project_id, id=job_instance_id).first()
    job_instance.enabled = -1 if job_instance.enabled == 0 else 0
    db.session.commit()
    return redirect(request.referrer, code=302)


@app.route("/project/<project_id>/spider/dashboard")
def spider_dashboard(project_id):
    spider_instance_list = SpiderInstance.list_spiders(project_id)
    return render_template("spider_dashboard.html",
                           spider_instance_list=spider_instance_list)


@app.route("/project/<project_id>/spider/deploy")
def spider_deploy(project_id):
    project = Project.find_project_by_id(project_id)
    return render_template("spider_deploy.html")


@app.route("/project/<project_id>/spider/upload", methods=['post'])
def spider_egg_upload(project_id):
    project = Project.find_project_by_id(project_id)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.referrer)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.referrer)
    if file:
        filename = secure_filename(file.filename)
        dst = os.path.join(tempfile.gettempdir(), filename)
        file.save(dst)
        agent.deploy(project, dst)
        flash('deploy success!')
    return redirect(request.referrer)


@app.route("/project/<project_id>/project/stats")
def project_stats(project_id):
    project = Project.find_project_by_id(project_id)
    run_stats = JobExecution.list_run_stats_by_hours(project_id)
    return render_template("project_stats.html", run_stats=run_stats)


@app.route("/project/<project_id>/server/stats")
def service_stats(project_id):
    project = Project.find_project_by_id(project_id)
    run_stats = JobExecution.list_run_stats_by_hours(project_id)
    return render_template("server_stats.html", run_stats=run_stats)


@app.route("/data", methods=["GET"])
def getdata():
    db = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    db.autocommit(True)
    c = db.cursor()
    c.execute("SELECT time,mem_usage FROM stat")
    ones = [[i[0]*1000,i[1]] for i in c.fetchall()]
    return "%s(%s);" % (request.args.get('callback'), json.dumps(ones))


@app.route("/mon", methods=["GET", "POST"])
def hello():
    db = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    db.autocommit(True)
    c = db.cursor()
    sql = ""
    if request.method == "POST":
        data = request.json
        try:
            sql = "INSERT INTO stat (host,mem_free,mem_usage,mem_total,time) VALUES('%s', '%s', '%s', '%s', '%d')" % (data['Host'], data['MemFree'], data['MemUsage'], data['MemTotal'], int(data['Time']))
            ret = c.execute(sql)
        except mdb.IntegrityError:
            print("error")
        return "OK"
    else:
        return render_template("mon.html")


@app.route("/cpu", methods=["GET"])
def cpu_index():
    return render_template("cpu.html")


@app.route("/cpu/index", methods=["POST"])
def cpu():
    db = mdb.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="wulispider", charset='utf8')
    db.autocommit(True)
    c = db.cursor()
    if request.method == "POST":
        sql ="SELECT * FROM cpu WHERE id>="+str(int(request.form['id']) + 1)
        c.execute(sql)
        res = c.fetchall()
    return jsonify(insert_time=[x[1] for x in res],
                   cpu=[x[2] for x in res],
                   )  # 返回json格式数据