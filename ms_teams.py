import pymsteams

def send_teams_msg(webhook_url, msg):
    for unit in msg:
        teams_msg = pymsteams.connectorcard(webhook_url)
        teams_msg.title(f"New Updates in {unit['unit_name']}")
        msg_count = 0

        
        for task in unit['tasks']:
            task_section = pymsteams.cardsection()

            task_section.title(f"**{task['task_name']}**")

            task_msgs = [f"**{t['timestamp']}** - {t['comment']}" for t in task['messages']]
            task_section.text("\n\n".join(task_msgs))
            teams_msg.addSection(task_section)
            msg_count += len(task['messages'])

        teams_msg.text(f"{msg_count} new messages")
        teams_msg.send()
