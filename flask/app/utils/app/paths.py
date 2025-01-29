import os


def get_root_directory():
    import app

    return "/".join(app.__file__.split("/")[:-2])


def get_migrations_dir(name):
    return os.path.join(get_root_directory(), name)


def get_dot_env_path():
    return os.path.join(get_root_directory(), ".env")
