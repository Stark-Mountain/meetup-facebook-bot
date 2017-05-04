from fabric.api import settings, local, abort, task
from fabric.contrib.console import confirm


def test():
    with settings(warn_only=True):
        result = local('python3 -m pytest tests', capture=True)
    if result.failed and not confirm('Tests failed. Continue anyway?'):
        abort('Aborting at user request.')


def commit():
    with settings(warn_only=True):
        local('git add -i && git commit')


def push(branch):
    local('git push origin %s' % branch)


@task
def prepare_deploy(branch):
    test()
    commit()
    push(branch)
