API_URL = 'https://ontrack.deakin.edu.au/api'

class OntrackAPI:
    @staticmethod
    def get_teaching_periods():
        return API_URL + '/teaching_periods'

    @staticmethod
    def get_projects():
        return API_URL + '/projects'

    @staticmethod
    def get_project(project_id):
        return API_URL + f'/projects/{project_id}'

    @staticmethod
    def get_unit_information(unit_id):
        return API_URL + f'/units/{unit_id}'

    @staticmethod
    def request_extension(project_id, task_def_id):
        return API_URL + f'/projects/{project_id}/task_def_id/{task_def_id}/request_extension'

    @staticmethod
    def get_task_comments(project_id, task_def_id):
        return API_URL + f'/projects/{project_id}/task_def_id/{task_def_id}/comments'

    @staticmethod
    def set_comment_to_unread(project_id, task_def_id, comment_id):
        return API_URL + f'/projects/{project_id}/task_def_id/{task_def_id}/comments/{comment_id}'

    @staticmethod
    def refresh_token():
        return API_URL + f'/auth'

    @staticmethod
    def get_task_pdf(unit_id, task_def_id):
        return API_URL + f'/units/{unit_id}/task_definitions/{task_def_id}/task_pdf.json'
