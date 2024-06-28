import subprocess
# subprocess.run(['pip','install', '-r', 'requirements.txt'])

from dotenv import load_dotenv
from openai import OpenAI
import json
import schedule
import time as tm
import datetime as dt
import os
from tabulate import tabulate

path = './assistants'
if not os.path.exists(path):
    os.mkdir(path)

load_dotenv()
client = OpenAI()

def make_dict(assistant_obj):
    """ gets the assistant object and returns a dictionary"""
    assistant_dict = {}
    for data in assistant_obj:
        key = data[0]
        value = str(data[1])

        if key == 'tool_resources' or key == 'tools':
            split = str(value).split(',')
            assistant_dict[f"{key}_not_split"] = value
            value = [{'.': line} for line in split]
            assistant_dict[f"{key}_split"] = value
            continue

        if key == 'instructions':
            split = str(value).split('\n')
            assistant_dict[f"{key}_not_split"] = value
            value = [{'.': line} for line in split]
            assistant_dict[f"{key}_split"] = value
            continue

        assistant_dict[f"{key}"] = value
    return assistant_dict

def list_assistants():
    # read assistants from OPENAI API as a list (REED RED don't get confused)
    gotten_assistants = client.beta.assistants.list(
        order="desc",
        limit=20,
    )

    # for pretty-printing the status of assistants in the console
    to_print_heads = ["NAME OF ASSISTANT", "ID STARTS WITH", 'STATUS']
    to_print=[]


    # loop through assistant objects obtained from OPENAI API to check their existence and change in their content compared to saved local files
    for assistant in gotten_assistants:
        # make the assistant object to a dict for becoming JSON serializable
        assistant_dict = make_dict(assistant)
        file_path = f'assistants/{assistant.name}_withID_{assistant.id}.json'

        # check if assistant file exists
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf8') as f:
                current_content = json.load(f)

                # check if their content are the same or has changed, if yes continue (ignore the rest and jump to the next iteration)
                current_content_str = json.dumps(current_content, ensure_ascii=False,  indent=4)
                assistant_dict_str = json.dumps(assistant_dict, ensure_ascii=False,  indent=4)
                if assistant_dict_str == current_content_str:
                    to_print.append([assistant.name, assistant.id[:10], 'same'])
                    continue
                else:
                    to_print.append([assistant.name, assistant.id[:10],'changed'])

        else:
            to_print.append([assistant.name, assistant.id[:10],'not found, added'])


        # rewrite the file (this will only be ignored by 'continue' above)
        with open(file_path, 'w', encoding='utf8') as f:
            json.dump(assistant_dict,f, ensure_ascii=False,  indent=4)

    # pretty-print assistant name, beginning of its ID (to differentiate those with the same name) and their status
    print(tabulate(to_print, headers=to_print_heads, tablefmt='fancy_grid', stralign= 'left'))


def all_tasks():
    """all the tasks that need to be run over and over by scheduling"""
    list_assistants()
    subprocess.run(['git','status'])
    subprocess.run(['git', 'add', '*'])
    subprocess.run(['git', 'commit','-m',f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}"])
    subprocess.run(['git','push', 'https://github.com/sirSaliYaRi/VARLOG.git'])

all_tasks()


# schedule.every(10).seconds.do(all_tasks)
#
# while True:
#     schedule.run_pending()
#     print("run done")
#     tm.sleep(2)
#     print("sleep done")