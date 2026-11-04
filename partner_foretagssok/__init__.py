from . import models


def post_init_hook(env):
    env['res.config.settings'].load_env_api_key()
