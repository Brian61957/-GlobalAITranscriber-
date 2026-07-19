import json
import os
from datetime import datetime

DB_FILE = "database/projects.json"


def load_projects():
    if not os.path.exists(DB_FILE):
        return []

    with open(DB_FILE, "r") as file:
        return json.load(file)


def save_project(url):

    projects = load_projects()

    project = {
        "url": url,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    projects.append(project)

    with open(DB_FILE, "w") as file:
        json.dump(projects, file, indent=4)