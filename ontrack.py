import requests
import json
import datetime
import urllib.parse

class Ontrack:
    def __init__(self, auth_token, emailer):
        self.auth_token = auth_token
        self.emailer = emailer

    def send_payload_with_request(self, url, data):
        session = requests.Session()
        r = session.post(url, params={'auth_token': self.auth_token}, data=data)
        res = json.loads(r.text)
        session.close()
        return res

    def get_api_json(self, url):
        session = requests.Session()
        r = session.get(url, params={'auth_token': self.auth_token})
        res = json.loads(r.text)
        session.close()
        return res

    def get_current_teaching_period(self):
        url = 'https://ontrack.deakin.edu.au/api/teaching_periods'
        periods = self.get_api_json(url)
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
        for proj in self.get_api_json(url):
            if proj['teaching_period_id'] == current_period_id:
                units.append(proj)

        return units

    # get information for a unit
    def get_project(self, proj_id):
        url = 'https://ontrack.deakin.edu.au/api/projects/{}'.format(proj_id)
        return self.get_api_json(url)

    # get all released tasks for a unit
    def get_project_tasks(self, proj_id):
        proj = self.get_project(proj_id)
        return proj['tasks']

    # get detailed task information for a unit
    def get_task_definitions(self, unit_id):
        url = 'https://ontrack.deakin.edu.au/api/units/{}'.format(unit_id)
        info = self.get_api_json(url)
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
        data = {'comment':comment, 'weeks_requested':weeks_requested}
        response = self.send_payload_with_request('https://ontrack.deakin.edu.au/api/projects/{}/task_def_id/{}/request_extension'.format(proj_id, task_def_id), data)
        return response

    # get all new comments for a task
    def get_new_task_comments(self, proj_id, task_def_id):
        task_info = self.get_api_json(
            'https://ontrack.deakin.edu.au/api/projects/{}/task_def_id/{}/comments'.format(proj_id, task_def_id))
        comments = []
        for task in task_info:
            if task['is_new']:
                comments.append(task['comment'])

        return comments

    def get_updated_email(self):
        email = 'You have some updates!\n\n'
        update_count = 0
        for p in self.get_projects():
            u_name = p['unit_name']
            first = True

            updated_content = self.get_updated_tasks(p)
            for name, updates in updated_content.items():
                if updates:
                    if first:
                        email += '{}\n\n'.format(u_name)
                        first = False

                    email += '{}\n'.format(name)
                    for update in updates:
                        email += ' - {}\n'.format(update)
                        update_count += 1

                email += '\n'

        if not first:
            self.emailer.send_ontrack_msg(email, update_count)
        else:
            print("No updates to email")

        
