import time
import logging

from yoci.travis.travis import Builds
from yoci.travis.travis import Job

lgr = logging.getLogger('travis_func_api')
lgr.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s-%(name)s[%(levelname)s] - '
                              '%(message)s')
console_handler.setFormatter(formatter)
lgr.addHandler(console_handler)


def _wait_for_build_state(build_id, end):
    builds = Builds(lgr)
    lgr.info('Waiting for build with ID {0} to reach final state for {1} '
             'seconds.'.format(build_id, int(end-time.time())))
    while time.time() < end:
        build = builds.show_build(id=build_id)
        state = build['state']
        if state != 'passed' and state != 'failed':
            lgr.info(
                'Build still in progress. Waiting for build process to end. '
                'Current build state is: ' + state)
            time.sleep(10)
        else:
            lgr.info('Build matching ID {0} has reached a final state: {1}'
                     .format(build_id, state))
            return build

    lgr.warn('Failed waiting for build state to reach passed/failed. Build '
             'state is {0}'.format(build['state']))


def _wait_for_commit(repo_name, branch_name, sha_id, end):
    builds = Builds(lgr, repo=repo_name)
    lgr.info('Waiting for commit with sha ID {0} and repo {1} and branch {2}'
             ' for: {3} seconds.'
             .format(sha_id, repo_name, branch_name, int(end-time.time())))
    while time.time() < end:
        builds_list, commits = builds.list_builds()
        for commit in commits:
            if commit['sha'] == sha_id and commit['branch'] == branch_name:
                lgr.info('Commit matching sha ID {0} was found'.format(sha_id))
                return commit

        lgr.info('Commit with sha ID {0} was not found. Waiting for 10 seconds'
                 .format(sha_id, repo_name))
        time.sleep(10)

    lgr.warning('Failed waiting for commit with sha ID {0} on repo {1} and '
                'branch {2}'.format(sha_id, repo_name, branch_name))


def _get_commit_id(repo_name, sha_id, end, branch_name=None):
    commit = _wait_for_commit(repo_name, branch_name, sha_id, end)
    if not commit:
        raise RuntimeError(
            'Failed waiting for commit with sha ID {0} on repo {1} and branch '
            '{2}'.format(sha_id, repo_name, branch_name))

    return commit['id']


def _get_build_with_id(builds, commit_id):
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
                    The name of the branch the commit was made to.
    :param timout_min:
                    The timeout to wait for a build to reach final state.
                    Default is set to 15 minutes.
    :return: a dictionary containing job results for the specified commit
    '''
    end = time.time() + 60 * timeout_min

    commit_id = _get_commit_id(repo_name, sha_id, end, branch_name=branch_name)

    builds = Builds(lgr, repo=repo_name)
    builds_list, commits = builds.list_builds()
    build_id = _get_build_with_id(builds_list, commit_id)

    # We wait for the build to reach final state.
    build = _wait_for_build_state(build_id, end)
    if build:
        job_ids = build['job_ids']
    else:
        raise RuntimeError('Failed waiting for build process to finish'
                           ' for the duration of {0}'
                           .format(timeout_min))

    jobs_state = dict()
    lgr.info('Getting jobs state for build with ID {0}'.format(build_id))
    for job_id in job_ids:
        job = Job(lgr, job_id=job_id).show_job()
        jobs_state.update({job['config']['env']: job['state']})
    return jobs_state
