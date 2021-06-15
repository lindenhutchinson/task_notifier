import requests
import json
import datetime
import urllib.parse
import random
from ontrack_api import OntrackAPI


class RequestsManager:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    def get(self, url, params={}):
        params.update({'auth_token': self.auth_token})
        resp = requests.get(url, params=params)
        resp.close()
        return json.loads(resp.text)

    def post(self, url, data=[], params={}):
        params.update({'auth_token': self.auth_token})
        resp = requests.post(url, params=params, data=data)
        resp.close()
        return json.loads(resp.text)

    def put(self, url, params):
        resp = requests.put(url, params=params)
        resp.close()
        return json.loads(resp.text)


class OntrackCtrl:
    def __init__(self, username, auth_token, use_all_units=False):
        self.username = username
        self.auth_token = auth_token
        self.use_all_units = use_all_units
        self.requests = RequestsManager(auth_token)

    def get_current_teaching_period(self):
        teaching_periods = self.requests.get(OntrackAPI.get_teaching_periods())
        now = datetime.datetime.now()
        current = 0
        for period in teaching_periods:
            start = datetime.datetime.strptime(
                period['start_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.datetime.strptime(
                period['end_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if now > start and now < end:
                current = period

        return current

    def get_projects(self):
        current_period_id = self.get_current_teaching_period()['id']
        active_units = []
        projects = self.requests.get(OntrackAPI.get_projects())
        for proj in projects:
            # if you want to search through all units for new messages (for testing while not having any active ontrack units)
            if self.use_all_units:
                active_units.append(proj)
            else:
                if proj['teaching_period_id'] == current_period_id:
                    active_units.append(proj)

        return active_units

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
                created_at = datetime.datetime.strptime(
                    comment['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")

                comments.append({
                    'timestamp': created_at.strftime("%d/%m/%y %X"),
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

            self.requests.post(OntrackAPI.set_comment_to_unread(
                msg['proj_id'], msg['task_id'], msg['msg_id']))

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

    def refresh_auth_token(self):
        resp = self.requests.put(OntrackAPI.refresh_auth_token(self.auth_token), params={
                                 'username': self.username, 'remember': True})

        if 'error' in resp.keys():
            return False

        self.auth_token = resp['auth_token']
        return resp['auth_token']
