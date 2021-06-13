import requests
import json
import datetime
import urllib.parse
import random

class Ontrack:
    def __init__(self, username, auth_token):
        self.username = username
        self.auth_token = auth_token

    def make_post_request(self, url, data):
        session = requests.Session()
        r = session.post(
            url, params={'auth_token': self.auth_token}, data=data)
        res = json.loads(r.text)
        session.close()
        return res

    def make_get_request(self, url):
        session = requests.Session()
        r = session.get(url, params={'auth_token': self.auth_token})
        res = json.loads(r.text)
        session.close()
        return res

    def make_put_request(self, url, params):
        session = requests.Session()
        r = session.put(url, params=params)
        res = json.loads(r.text)
        session.close()
        return res

    def get_current_teaching_period(self):
        url = 'https://ontrack.deakin.edu.au/api/teaching_periods'
        periods = self.make_get_request(url)
        now = datetime.datetime.now()
        current = 0
        for period in periods:
            start = datetime.datetime.strptime(
                period['start_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            end = datetime.datetime.strptime(
                period['end_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if now > start and now < end:
                current = period

        return current

    # find all units for the current trimester
    def get_projects(self):
        url = 'https://ontrack.deakin.edu.au/api/projects'
        units = []
        current_period_id = self.get_current_teaching_period()['id']
        for proj in self.make_get_request(url):
            # If you want to get ontrack data from units of all teaching periods, you can comment the line below
            if proj['teaching_period_id'] == current_period_id:
                units.append(proj)

        return units

    # get information for a unit
    def get_project(self, proj_id):
        url = 'https://ontrack.deakin.edu.au/api/projects/{}'.format(proj_id)
        return self.make_get_request(url)

    # get all released tasks for a unit
    def get_project_tasks(self, proj_id):
        proj = self.get_project(proj_id)
        return proj['tasks']

    # get detailed task information for a unit
    def get_task_definitions(self, unit_id):
        url = 'https://ontrack.deakin.edu.au/api/units/{}'.format(unit_id)
        info = self.make_get_request(url)
        return info['task_definitions']

    # get a specific task's name
    def get_task_name(self, task_def, task_def_id):
        for task in task_def:
            if task['id'] == task_def_id:
                return ("{} : {}".format(task['abbreviation'], task['name']))

        return "Couldn't find name..."


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
        data = {'comment': comment, 'weeks_requested': weeks_requested}
        response = self.make_post_request(
            'https://ontrack.deakin.edu.au/api/projects/{}/task_def_id/{}/request_extension'.format(proj_id, task_def_id), data)
        return response

    # get all new comments for a task
    def get_new_task_comments(self, proj_id, task_def_id):
        task_info = self.make_get_request(
            'https://ontrack.deakin.edu.au/api/projects/{}/task_def_id/{}/comments'.format(proj_id, task_def_id))
        comments = []
        for task in task_info:
            if task['is_new']:
                comments.append(task['comment'])

        return comments

    def get_task_comment_ids(self, proj_id, task_def_id):
        task_info = self.make_get_request(
            'https://ontrack.deakin.edu.au/api/projects/{}/task_def_id/{}/comments'.format(proj_id, task_def_id))
        id_list = []
        for task in task_info:
            if task['author']['email'].split('@')[0] == self.username:
                continue
            
            id_list.append(task['id'])

        return id_list

    def set_random_tasks_unread(self, num=1):
        projects = self.get_projects()
        messages = []
        for proj in projects:
            tasks = self.get_task_definitions(proj['unit_id'])
            for task in tasks:
                id_list = self.get_task_comment_ids(proj['project_id'], task['id'])
                for id in id_list:
                    messages.append({
                        'proj_id':proj['project_id'],
                        'task_id':task['id'],
                        'msg_id':id
                    })
        set_unread = num if num <= len(messages) else len(messages)
        for i in range(set_unread):
            msg = random.choice(messages)
            self.mark_comment_unread(msg['proj_id'], msg['task_id'], msg['msg_id'])
            messages.remove(msg)

    def mark_comment_unread(self, proj_id, task_def_id, comment_id):
        url = f"https://ontrack.deakin.edu.au/api/projects/{proj_id}/task_def_id/{task_def_id}/comments/{comment_id}"
        self.make_post_request(url, {})

    def get_update_msg(self):
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
        url = f"https://ontrack.deakin.edu.au/api/auth/{self.auth_token}"
        resp = self.make_put_request(
            url, {'username': self.username, 'remember': True})
        if 'error' in resp.keys():
            return False

        self.auth_token = resp['auth_token']
        return resp['auth_token']
