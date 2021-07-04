class OntrackAPI:
    @staticmethod
    def get_teaching_periods():
        return 'https://ontrack.deakin.edu.au/api/teaching_periods'

    @staticmethod
    def get_projects():
        return 'https://ontrack.deakin.edu.au/api/projects'

    @staticmethod
    def get_project(project_id):
        return f'https://ontrack.deakin.edu.au/api/projects/{project_id}'

    @staticmethod
    def get_unit_information(unit_id):
        return f'https://ontrack.deakin.edu.au/api/units/{unit_id}'

    @staticmethod
    def request_extension(project_id, task_def_id):
        return f'https://ontrack.deakin.edu.au/api/projects/{project_id}/task_def_id/{task_def_id}/request_extension'

    @staticmethod
    def get_task_comments(project_id, task_def_id):
        return f'https://ontrack.deakin.edu.au/api/projects/{project_id}/task_def_id/{task_def_id}/comments'

    @staticmethod
    def set_comment_to_unread(project_id, task_def_id, comment_id):
        return f"https://ontrack.deakin.edu.au/api/projects/{project_id}/task_def_id/{task_def_id}/comments/{comment_id}"

    @staticmethod
    def refresh_auth_token(auth_token):
        return f"https://ontrack.deakin.edu.au/api/auth/{auth_token}"

    @staticmethod
    def get_task_pdf(unit_id, task_def_id):
        return f"https://ontrack.deakin.edu.au/api/units/{unit_id}/task_definitions/{task_def_id}/task_pdf.json"