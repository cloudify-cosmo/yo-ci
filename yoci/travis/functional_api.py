import time
import logging

from yoci.travis.travis import Builds
from yoci.travis.travis import Job

lgr = logging.getLogger('test logger')


def _wait_for_build_state(build_id, end):
    builds = Builds(lgr)
    while time.time() < end:
        build = builds.show_build(id=build_id)
        state = build['state']
        if state != 'passed' and state != 'failed':
            lgr.info(
                'Build still in progress. Waiting for build process to end')
            time.sleep(10)
        else:
            return build

    lgr.warn('Failed waiting for build state to reach passed/failed. Build '
             'state is {0}'.format(build['state']))


def _wait_for_commit(repo_name, sha_id, end):
    builds = Builds(lgr, repo=repo_name)
    while time.time() < end:
        builds_list, commits = builds.list_builds()
        for commit in commits:
            if commit['sha'] == sha_id:
                return commit

        time.sleep(10)

    lgr.warn('Failed waiting for commit with sha ID {0} on repo {1} for the'
             ' duration of {2}ms'.format(sha_id, repo_name, time.time() - end))


def _get_commit_id(repo_name, sha_id, end, branch_name=None):
    commit = _wait_for_commit(repo_name, sha_id, end)
    if not commit:
        raise RuntimeError(
            'Failed waiting for commit with sha ID {0} on repo {1} for the'
            ' duration of {2}ms'.format(sha_id, repo_name, time.time() - end))

    # For validation reasons. branch not required with sha_id
    if branch_name and branch_name != commit['branch']:
        raise RuntimeError('Commit with sha_id {0} was made to branch'
                           ' {1}. Expecting branch {2}'
                           .format(sha_id, commit['branch'], branch_name))
    return commit['id']


def _get_build_id(builds, commit_id):
    build_id = None
    for build in builds:
        if build['commit_id'] == commit_id:
            build_id = build['id']
            break
    return build_id


def get_jobs_status(sha_id, repo_name, branch_name=None, timeout_min=15):
    '''
    Returns a dictionary containing job results for the specified commit and
    repository name
    :param sha_id:
                    The unique commit SHA ID.
    :param repo_name:
                    The name of the repo the commit was made to.
    :param branch_name:
                    The name of the branch the commit was made to
                    Used mostly for validation.Ignored if not passed.
    :param timout_min:
                    The timeout to wait for a build to reach final state.
                    Default is set to 15 minutes.
    :return: a dictionary containing job results for the specified commit
    '''
    end = end = time.time() + 60 * timeout_min

    commit_id = _get_commit_id(repo_name, sha_id, end, branch_name=branch_name)

    if commit_id is None:
        raise RuntimeError('Could not find commit matching to sha {0} for repo'
                           ' {1}'.format(sha_id, repo_name))

    builds = Builds(lgr, repo=repo_name)
    builds_list, commits = builds.list_builds()
    build_id = _get_build_id(builds_list, commit_id)

    # We wait for the build to reach final state.
    build = _wait_for_build_state(build_id, end)
    if build:
        job_ids = build['job_ids']
    else:
        raise RuntimeError('Failed waiting for build process to finish'
                           ' for the duration of {0}'
                           .format(timeout_min))

    jobs_state = dict()
    for job_id in job_ids:
        job = Job(lgr, job_id=job_id).show_job()
        jobs_state.update({job['config']['env']: job['state']})
    return jobs_state


# jobs_state = get_jobs_status('40509789b11d1bf7cb4c785162cb77f9ea927274',
#                              'cloudify-cosmo/packman',
#                              branch_name='master',
#                              timeout_min=15)

jobs_state = get_jobs_status('7d86b25c3cf50b6ed6d754ef7917fc8764dc5f41',
                                                        'cloudify-cosmo/cloudify-dsl-parser',
                                                        branch_name='master',
                                                        timeout_min=2)
