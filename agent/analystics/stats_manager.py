from database.history_manager import load_projects


def get_total_projects():
    return len(load_projects())


def get_total_languages():
    return 0


def get_total_hours():
    return 0


def get_average_confidence():
    return 0