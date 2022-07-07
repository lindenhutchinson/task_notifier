import requests
import json
from datetime import datetime
import urllib.parse
import random
from .ontrack_api import OntrackAPI


class RequestsManager:
    def __init__(self, auth_token, username):
        self.headers = {'Auth_Token': auth_token, 'Username': username}

    def get(self, url, params={}):
        resp = requests.get(url, params=params, headers=self.headers)
        resp.close()
        return json.loads(resp.text)

    def get_content(self, url, params={}):
        resp = requests.get(url, params=params, stream=True, headers=self.headers)
        return resp.content

    def post(self, url, data=[], params={}):
        if not params:
            params = self.headers
        resp = requests.post(url, params=params, data=data, headers=self.headers)
        resp.close()

        return json.loads(resp.text)

    def put(self, url, data=[], params={}):
        resp = requests.put(url, params=params, data=data, headers=self.headers)
        resp.close()
        return json.loads(resp.text)


class OntrackCtrl:
    def __init__(self, username, auth_token, use_all_units=False):
        self.username = username
        self.auth_token = auth_token
        self.use_all_units = use_all_units
        self.requests = RequestsManager(auth_token, username)

    def get_current_teaching_period(self):
        return 18 # Tri 2 2022
        teaching_periods = self.requests.get(OntrackAPI.get_teaching_periods())
        now = datetime.now()

        # reverse the array as the current period is most likely towards the end
        for period in teaching_periods[::-1]:
            start = datetime.strptime(
                period['start_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.strptime(
                period['end_date'], "%Y-%m-%dT%H:%M:%S.%fZ")

            # sorry DeakinCollege ;_;
            if now > start and now < end and 'DeakinCollege' not in period['period']:
                return period['id']

        raise Exception(
            "Couldn't find current teaching period (has the trimester started yet? set use_all_units to True if you just wanna see some messages)")

    def get_projects(self):
        projects = self.requests.get(OntrackAPI.get_projects())

        if self.use_all_units:
            return projects

        current_period_id = self.get_current_teaching_period()
        # projects have an "active" attribute, but that relates to whether or not they are currently being run
        # it is not related to the current student taking that unit
        return list(filter(lambda p: p['teaching_period_id'] == current_period_id, projects))

    # get all released tasks for a unit
    def get_project_tasks(self, proj_id):
        project = self.requests.get(OntrackAPI.get_project(proj_id))
        return project['tasks']

    # get detailed task information for a unit
    def get_task_definitions(self, unit_id):
        unit_data = self.requests.get(OntrackAPI.get_unit_information(unit_id))
        return unit_data['task_definitions']

    # get a specific task's name
    def get_task_name(self, task_definitions, task_def_id):
        task = [t for t in task_definitions if t['id'] == task_def_id][0]
        return f"{task['abbreviation']} - {task['name']}"

    # get all tasks that have new comments
    def get_updated_tasks(self, proj):
        updates = {}
        task_defs = self.get_task_definitions(proj['unit_id'])
        tasks = self.get_project_tasks(proj['project_id'])

        for task in tasks:
            if task['num_new_comments'] > 0:
                comments = self.get_new_task_comments(
                    proj['project_id'], task['task_definition_id'])

                name = self.get_task_name(
                    task_defs, task['task_definition_id'])

                updates.update({name: comments})

        return updates

    def request_extension(self, proj_id, task_def_id, comment, weeks_requested):
        resp = self.requests.post(OntrackAPI.request_extension(proj_id, task_def_id), data={
                                  'comment': comment, 'weeks_requested': weeks_requested})
        return resp

    # get all new comments for a task
    def get_new_task_comments(self, proj_id, task_def_id):
        task_comments = self.requests.get(
            OntrackAPI.get_task_comments(proj_id, task_def_id))

        comments = []
        for comment in task_comments:
            if comment['is_new']:
                created_at = datetime.strptime(
                    comment['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")

                comments.append({
                    'timestamp': created_at.strftime("%d/%m/%y %I:%M%p"),
                    'comment': comment['comment']
                })

        return comments

    # used for randomly setting comments to unread
    def get_task_comment_ids(self, proj_id, task_def_id):
        task_comments = self.requests.get(
            OntrackAPI.get_task_comments(proj_id, task_def_id))

        id_list = []
        for comment in task_comments:
            # check that the comment isn't from ourselves and that it is a real message
            if comment['author']['email'].split('@')[0] != self.username and comment['type'] == 'text':
                id_list.append(comment['id'])

        return id_list

    def set_random_tasks_unread(self, num=1):
        projects = self.get_projects()
        messages = []
        for proj in projects:
            tasks = self.get_task_definitions(proj['unit_id'])
            for task in tasks:
                id_list = self.get_task_comment_ids(
                    proj['project_id'], task['id'])
                for id in id_list:
                    messages.append({
                        'proj_id': proj['project_id'],
                        'task_id': task['id'],
                        'msg_id': id
                    })
        set_unread = num if num <= len(messages) else len(messages)
        for i in range(set_unread):
            msg = random.choice(messages)

            resp = self.requests.post(OntrackAPI.set_comment_to_unread(msg['proj_id'], msg['task_id'], msg['msg_id']))

            messages.remove(msg)

    def get_updates_msg(self):
        update_data = []

        for p in self.get_projects():
            data = {
                'unit_name': p['unit_name'],
                'tasks': []
            }
            updated = False

            updated_content = self.get_updated_tasks(p)
            for name, updates in updated_content.items():
                if updates:
                    updated = True
                    data['tasks'].append({
                        'task_name': name,
                        'messages': updates
                    })

            if updated:
                update_data.append(data)

        return update_data

    def get_unit_tasks_pdf(self):
        # if self.use_all_units:
        #     raise Exception(
        #         "You probably don't want to download ALL of the task PDF files from ALL your former units, right? (set use_all_units to False)")

        projects = self.get_projects()
        tasks = {}
        for proj in projects:
            unit_code = proj['unit_code']

            if len(proj['unit_code'].split('/')) > 1:
                unit_code = proj['unit_code'].split('/')[0]

 
            tasks.update({unit_code: []})
            task_defs = self.get_task_definitions(proj['unit_id'])
            for task in task_defs:
                resp = self.requests.get_content(
                    OntrackAPI().get_task_pdf(proj['unit_id'], task['id']))

                task_name =  f"{task['abbreviation']}"
                task_name = task_name.replace('\\','-').replace('/','-')
                tasks[unit_code].append({
                    'name':task_name,
                    'content': resp
                })

        return tasks

