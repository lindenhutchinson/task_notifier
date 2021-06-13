import pymsteams

def send_teams_msg(webhook_url, msg):
    for unit in msg:
        teams_msg = pymsteams.connectorcard(webhook_url)
        teams_msg.title(f"New Updates in {unit['unit_name']}")
        msg_count = 0

        
        for task in unit['tasks']:
            task_section = pymsteams.cardsection()

            task_section.title(f"Task: {task['task_name']}")
            task_section.text("\n\n".join(task['messages']))
            teams_msg.addSection(task_section)
            msg_count += len(task['messages'])

        teams_msg.text(f"{msg_count} new messages")
        teams_msg.send()
