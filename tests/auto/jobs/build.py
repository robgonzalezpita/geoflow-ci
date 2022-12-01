"""
Name: build.py
Python to clone and build a repo and if requested run
Integration tests.
"""

# Imports
import datetime
import logging
import time
import os
from configparser import ConfigParser as config_parser


def run(job_obj):
    """
    Runs a CI test for a PR
    """
    logger = logging.getLogger('BUILD/RUN')
    pr_repo_loc, repo_dir_str = clone_pr_repo(job_obj, job_obj.workdir)
    build_script_loc = pr_repo_loc + '/GeoFLOW/ci_tests'
    log_name = pr_repo_loc + '/build/build.out'
    # passing in machine for build
    create_build_commands = [[f'./build.sh'
                              f' >& {log_name}',
                             build_script_loc]]
    logger.info('Running test build script')
    job_obj.run_commands(logger, create_build_commands)
    # Read the build log to see whether it succeeded
    build_success = post_process(job_obj, build_script_loc, log_name,
                                 pr_repo_loc)
    logger.info('After build post-processing')
    logger.info(f'Action: {job_obj.preq_dict["action"]}')
    # Comments have not yet been written
    issue_id = 0
    if build_success:
        job_obj.comment_append('Build was Successful')
        if job_obj.preq_dict["action"] == 'int':
            # See if a previous job on same PR is still running
            cfg_file = 'Longjob.cfg'
            # See if there are any tests already running for this PR
            if os.path.exists(cfg_file):
                config = config_parser()
                config.read(cfg_file)
                num_sections = len(config.sections())
                num_tests = 0
                # Remove any older tests with the same PR ID
                for ci_log in config.sections():
                    if str(job_obj.preq_dict["preq"].id) in ci_log:
                        num_tests = num_tests + 1
                        config.remove_section(ci_log)
                # If those were the only tests, delete the file
                if num_sections == num_tests:
                    os.remove(cfg_file)
                    # Still need to remove cron jobs and maybe output dirs
                    # Maybe write a message to PR (older issue id)
            # Start the workflow process
            expt_script_loc = pr_repo_loc + '/ci_tests/integration_tests'
            expts_base_dir = os.path.join(repo_dir_str, 'expt_dirs')
            log_name = 'expt.out'
            integration_script = expt_script_loc + '/integration_tests.sh'
            if os.path.exists(integration_script):
                logger.info('Running integration test')
                create_expt_commands = \
                    [[f'./integration_tests.sh >&'
                      f'{log_name}', expt_script_loc]]
                job_obj.run_commands(logger, create_expt_commands)
                # logger.info('After end_to_end script')
                # # no experiment dir or no test dirs in it suggests error
                # if os.path.exists(expts_base_dir) and len(os.listdir(expts_base_dir)):
                #     job_obj.comment_append('Rocoto jobs started')
                #     # If workflow running, comments will be written
                #     issue_id = process_expt(job_obj, expts_base_dir)
                # else:
                #     setup_log = os.path.join(expt_script_loc, log_name)
                #     if os.path.exists(setup_log):
                #         process_setup(job_obj, setup_log)
                #     gen_log_loc = pr_repo_loc + '/ush'
                #     gen_log_name = 'log.generate_FV3LAM_wflow'
                #     process_gen(job_obj, gen_log_loc, gen_log_name)
            else:
                job_obj.comment_append(f'Script {integration_script} '
                                       'does not exist in repo')
                job_obj.comment_append('Cannot run Integration tests')
    else:
        job_obj.comment_append('Build Failed')

    # Only write out comments if not already written after workflow running
    if issue_id == 0:
        issue_id = job_obj.send_comment_text()
        logger.debug(f'Issue comment id is {issue_id}')


def clone_pr_repo(job_obj, workdir):
    ''' clone the GitHub pull request repo, via command line '''
   
    logger = logging.getLogger('BUILD/CLONE_PR_REPO')

    # These are for the new/head repo in the PR
    new_repo = job_obj.preq_dict['preq'].head.repo.full_name
    new_branch = job_obj.preq_dict['preq'].head.ref
   
    # The new repo is the default repo
    git_url = f'https://${{ghapitoken}}@github.com/{new_repo}'


    logger.info(f'GIT URL: {git_url}')
    logger.info(f'app branch: {new_branch}')
    logger.info('Starting repo clone')
    repo_dir_str = f'{workdir}/'\
                   f'{str(job_obj.preq_dict["preq"].id)}/'\
                   f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
    pr_repo_loc = f'{repo_dir_str}'
    job_obj.comment_append(f'Repo location: {pr_repo_loc}')

    create_repo_commands = [
        [f'mkdir -p "{repo_dir_str}"', os.getcwd()],
        [f'git clone -b {new_branch} {git_url}', repo_dir_str]]
    
    job_obj.run_commands(logger, create_repo_commands)

    logger.info('Finished repo clone')
    return pr_repo_loc, repo_dir_str


def post_process(job_obj, build_script_loc, log_name, pr_repo_loc):
    logger = logging.getLogger('BUILD/POST_PROCESS')
    ci_log = f'{build_script_loc}/{log_name}'
    geoflow_cdg = pr_repo_loc + '/build/bin/geoflow_cdg'
    build_succeeded = False

    if os.path.exists(ci_log):
        # was the executable created?
        if os.path.exists(geoflow_cdg): # and os.path.exists(enkf_exe):
            build_succeeded = True
        if build_succeeded:
            logger.info('Build was successful')
        else:
            logger.info('Build failed')
            job_obj.comment_append('Build failed')
            raise Exception('Build failed abruptly ')

        return build_succeeded
    else:
        logger.critical(f'Could not find {job_obj.machine}'
                        f'.{job_obj.compiler} '
                        f'{job_obj.preq_dict["action"]} log')
        raise FileNotFoundError
    

# def process_logfile(job_obj, ci_log):
#     """
#     Runs after code has been cloned and built
#     Checks to see whether build was successful or failed
#     """
#     logger = logging.getLogger('BUILD/PROCESS_LOGFILE')
#     fail_string = 'FAIL'
#     success_string = 'ALL BUILDS SUCCEEDED'
#     build_succeeded = False
#     if os.path.exists(ci_log):
#         with open(ci_log) as fname:
#             for line in fname:
#                 if fail_string in line:
#                     job_obj.comment_append(f'{line.rstrip()}')
#                 elif success_string in line:
#                     build_succeeded = True
#         if build_succeeded:
#             logger.info('Build was successful')
#         else:
#             logger.info('Build failed')
#             job_obj.comment_append('Build failed')
#             raise Exception('Build failed abruptly ')

#         return build_succeeded
#     else:
#         logger.critical(f'Could not find {job_obj.machine}'
#                         f'.{job_obj.compiler} '
#                         f'{job_obj.preq_dict["action"]} log')
#         raise FileNotFoundError


# def process_setup(job_obj, setup_log):
#     """
#     Runs after setup for a rocoto workflow
#     Checks to see if an error has occurred
#     """
#     logger = logging.getLogger('BUILD/PROCESS_SETUP')
#     error_string = 'ERROR'
#     setup_failed = False
#     with open(setup_log) as fname:
#         for line in fname:
#             if error_string in line:
#                 job_obj.comment_append('Setup for Workflow Failed')
#                 setup_failed = True
#                 logger.info('Setup for workflow failed')
#             if setup_failed:
#                 job_obj.comment_append(f'{line.rstrip()}')
#     if setup_failed:
#         raise Exception('Setup for workflow could not complete ')


# def process_gen(job_obj, gen_log_loc, gen_log_name):
#     """
#     Runs after a rocoto workflow has been generated
#     Checks to see if an error has occurred
#     """
#     logger = logging.getLogger('BUILD/PROCESS_GEN')
#     gen_log = f'{gen_log_loc}/{gen_log_name}'
#     error_string = 'ERROR'
#     error_msg = 'err_msg'
#     gen_failed = False
#     if os.path.exists(gen_log):
#         with open(gen_log) as fname:
#             for line in fname:
#                 if error_string in line or error_msg in line:
#                     job_obj.comment_append('Generating Workflow Failed')
#                     gen_failed = True
#                     logger.info('Generating workflow failed')
#                 if gen_failed:
#                     job_obj.comment_append(f'{line.rstrip()}')


# def process_expt(job_obj, expts_base_dir):
#     """
#     Runs after a rocoto workflow has been started to run one or more expts
#     Assumes that more expt directories can appear after this job has started
#     Checks for success or failure for each expt
#     """
#     logger = logging.getLogger('BUILD/PROCESS_EXPT')
#     expt_done = 0
#     # wait time for workflow is time_mult * sleep_time seconds
#     time_mult = 2
#     sleep_time = 6
#     repeat_count = time_mult
#     complete_expts = []
#     expt_list = os.listdir(expts_base_dir)
#     complete_string = "This cycle is complete"
#     failed_string = "DEAD"

#     # Set issue id for cases where workflow does not start
#     issue_id = 0

#     while (expt_done < len(expt_list)) and repeat_count > 0:
#         time.sleep(sleep_time)
#         repeat_count = repeat_count - 1
#         expt_list = os.listdir(expts_base_dir)
#         logger.info('Experiment dir after return of end_to_end')
#         logger.info(expt_list)
#         for expt in expt_list:
#             expt_log = os.path.join(expts_base_dir, expt,
#                                     'log/FV3LAM_wflow.log')
#             if os.path.exists(expt_log) and expt not in complete_expts:
#                 with open(expt_log) as fname:
#                     for line in fname:
#                         if complete_string in line:
#                             expt_done = expt_done + 1
#                             job_obj.comment_append(f'Experiment done: {expt}')
#                             job_obj.comment_append(f'{line.rstrip()}')
#                             logger.info(f'Experiment done: {expt}')
#                             complete_expts.append(expt)
#                         elif failed_string in line:
#                             expt_done = expt_done + 1
#                             job_obj.comment_append('Experiment failed: '
#                                                    f'{expt}')
#                             job_obj.comment_append(f'{line.rstrip()}')
#                             logger.info(f'Experiment failed: {expt}')
#                             complete_expts.append(expt)
#     logger.info(f'Wait Cycles completed: {time_mult - repeat_count}')
#     logger.info(f'Done: {len(complete_expts)} of {len(expt_list)}')

#     # If not all experiments completed, writes a list in a config file
#     if len(complete_expts) < len(expt_list):
#         job_obj.comment_append(f'Long term tracking will be done'
#                                f' on {len(expt_list)} experiments')

#         # Write out comments so far and save issue id for later appending
#         issue_id = job_obj.send_comment_text()
#         logger.debug(f'Issue comment id is {issue_id}')

#         undone = list(set(expt_list) - set(complete_expts))
#         config = config_parser()
#         file_name = 'Longjob.cfg'
#         if os.path.exists(file_name):
#             config.read(file_name)
#         for expt in undone:
#             expt_log = os.path.join(expts_base_dir, expt,
#                                     'log/FV3LAM_wflow.log')
#             logger.info(f'expt log: {expt_log}')
#             pr_repo = job_obj.repo["address"]
#             pr_num = job_obj.preq_dict['preq'].number
#             config[expt_log] = {}
#             config[expt_log]['expt'] = expt
#             config[expt_log]['machine'] = job_obj.machine
#             config[expt_log]['pr_repo'] = pr_repo
#             config[expt_log]['pr_num'] = str(pr_num)
#             config[expt_log]['issue_id'] = str(issue_id.id)
#         with open(file_name, 'w') as fname:
#             config.write(fname)

#     return issue_id
