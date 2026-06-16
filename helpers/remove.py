import warnings

def ignore_initial_userwarning():
    warnings.filterwarnings(
        "ignore",
        message="pkg_resources is deprecated as an API"
    )