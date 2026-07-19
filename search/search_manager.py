from database.history_manager import load_projects


def search_projects(keyword):

    projects = load_projects()

    if keyword == "":
        return projects

    results = []

    for project in projects:

        if keyword.lower() in project["url"].lower():
            results.append(project)

    return results