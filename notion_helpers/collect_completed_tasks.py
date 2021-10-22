import json
import logging
import os
from datetime import datetime

from notion.block import Block
from notion.client import Client, UnableToCompleteRequestException

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
LOG.addHandler(ch)

"""
- Get the contents of the daily tasks db
- Uncheck all the items in the daily tasks db
- Add all the completed Items into daily task history
"""


def config():
    config_items = [
        "NOTION_API_KEY",
        "NOTION_DAILY_TASK_DATABASE",
        "NOTION_TASK_HISTORY_DATABASE",
    ]
    config = {}
    for item in config_items:
        config[item] = os.getenv(item)
    return config


class CollectCompletedTasks:
    def __init__(self, cfg):
        self.cfg = cfg
        self.notion_client = Client(cfg["NOTION_API_KEY"])

    def get_daily_task_items_and_uncheck_them(self):
        def uncheck_item():
            return dict(properties=dict(Done=dict(checkbox=False)))

        try:
            database_id = self.cfg["NOTION_DAILY_TASK_DATABASE"]
            daily_task_db = self.notion_client.get_database_contents(database_id)

            results = json.loads(daily_task_db)["results"]
            tasks = []
            for result in results:
                time = result["properties"]["Time"]["rich_text"][0]["text"]["content"]
                name = result["properties"]["Name"]["title"][0]["text"]["content"]
                done = result["properties"]["Done"]["checkbox"]
                if done:
                    res = self.notion_client.update_page_content(
                        result["id"], json.dumps(uncheck_item())
                    )
                tasks.append((time, name, done))
            tasks.sort(key=lambda x: x[0])

        except UnableToCompleteRequestException as e:
            LOG.error(e)
            return None

        return tasks

    def add_all_completed_task_items_to_task_history(self, task_list):
        task_completion_emoji_map = {
            0: "🖕🏼🖕🏼🖕🏼🖕🏼",
            1: "🖕🏼🖕🏼🖕🏼",
            2: "🖕🏼🖕🏼",
            3: "🖕🏼",
            4: "🤏🏽🍆",
            5: "🙅🏼‍♀️",
            6: "⭐",
            7: "⭐⭐",
            8: "⭐⭐⭐",
            9: "🌟🌟🌟",
            10: "🎆🎆🎆🎆",
            11: "🎉🎆🌟🚀🌟🎆🎉",
            12: "🚀🚀⭐🚀🚀",
        }
        database_id = self.cfg["NOTION_TASK_HISTORY_DATABASE"]
        completed_task_blocks = [
            Block.text_block(f"{i} {j}") for i, j, k in task_list if k
        ]

        if len(completed_task_blocks) == 0:
            LOG.error("[!] this lazy piece of sh#T did not complete any tasks.")

        new_entry = dict(
            parent=dict(database_id=database_id),
            properties=dict(
                Name=dict(title=[dict(text=dict(content=f"{datetime.now().date()}"))]),
                Completion=dict(
                    rich_text=[
                        dict(
                            text=dict(
                                content=task_completion_emoji_map[
                                    len(completed_task_blocks)
                                ]
                            )
                        )
                    ]
                ),
            ),
            children=[Block.heading_1("Completed Tasks"), *completed_task_blocks],
        )

        try:
            self.notion_client.create_page(json.dumps(new_entry))
        except UnableToCompleteRequestException as e:
            LOG.error(e)
            return None

        return True


def main():
    LOG.info("[+] application started")
    cfg = config()
    LOG.info("[+] collecting tasks")
    cct = CollectCompletedTasks(cfg)
    task_list = cct.get_daily_task_items_and_uncheck_them()
    if task_list == None:
        # Since we did not manage to get any results from the API
        # We will quit the application
        return None
    LOG.info("[+] archiving tasks to task history table")
    cct.add_all_completed_task_items_to_task_history(task_list)
    LOG.info("[+] application finished")
