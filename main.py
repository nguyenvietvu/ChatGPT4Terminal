import os
import sys
from colorama import init, Fore, Style
from openai import OpenAI
import json
from enum import Enum
from dotenv import load_dotenv
load_dotenv()

FIRST_PROMT = "?"
SECOND_PROMT = "?"
COMMAND_QUIT = "x"
COMMAND_CLEAR = "c"
GPT_MODEL = "gpt-4-turbo-preview"
EMPTY=""
SPACE=" "
NEW_LINE="\n"
HISTORY_FILE = ".context.json"

class Role(Enum):
    user = 'user'
    assistant = 'assistant'
    system = 'system'

args = sys.argv[1:]

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Initialize colorama
init()

def save(context):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(context, file)

def clearContext():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

def loadContext():
    try:
        with open(HISTORY_FILE, 'r') as file:
            context = json.load(file) or []
    except FileNotFoundError:
        context = []
    return context

def addContent(context, role, content):
    context.append({'role': role, 'content': content})

def colored(color, message):
    return (f'{Style.NORMAL}{color}{message}{Style.RESET_ALL}')

def quit():
    clearContext()
    sys.exit()

def chat(role, content):
    context = loadContext()
    addContent(context, role, content)

    stream = client.chat.completions.create(
        model=GPT_MODEL,
        messages=context,
        stream=True,
    )
    gptContent = EMPTY
    gptRole = EMPTY
    for chunk in stream:
        gptContent += (chunk.choices[0].delta.content or EMPTY)
        if gptRole == EMPTY:
            gptRole = (chunk.choices[0].delta.role or EMPTY)
        print(colored(Fore.GREEN, (chunk.choices[0].delta.content or EMPTY)), end=EMPTY)

    if content != EMPTY and gptRole != EMPTY:
        addContent(context, gptRole, gptContent)
    save(context)

#***start***
try:
    content = EMPTY
    if len(args) > 0:
        content = SPACE.join(args)
        if content != EMPTY:
            chat(Role.user.value, content)
    else:
        content = input(colored(Fore.WHITE, NEW_LINE + FIRST_PROMT + ": "))
        while True:
            if content == COMMAND_QUIT:
                quit()
            elif content == COMMAND_CLEAR:
                clearContext()
            else:
                if content != EMPTY:
                    chat(Role.user.value, content)
                
            content = input(colored(Fore.WHITE, NEW_LINE + SECOND_PROMT + ": "))
except KeyboardInterrupt:
    quit()
