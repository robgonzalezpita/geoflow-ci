"""
Name: ci_long.py
This Python program reads a config file that has information
on Integration tests that were not completed, and
returns status information.

This script should be started through start_ci_py_pro.sh so that
env vars and Python paths are set up prior to start.
"""

from github import Github as gh

import datetime
import os
import logging
from configparser import ConfigParser as config_parser


class GHInterface:
    '''
    This class stores information for communicating with GitHub
    ...

    Attributes
    ----------
    GHACCESSTOKEN : str
      API token to authenticate with GitHub
    client : pyGitHub communication object
      The connection to GitHub to make API requests
    '''

    def __init__(self):
        self.logger = logging.getLogger('GHINTERFACE')

        filename = 'accesstoken'

        if os.path.exists(filename):
            if oct(os.stat(filename).st_mode)[-3:] != 600:
                with open(filename) as f:
                    os.environ['ghapitoken'] = f.readline().strip('\n')
            else:
                raise Exception('File permission needs to be "600" ')
        else:
            raise FileNotFoundError('Cannot find file "accesstoken"')

        try:
            self.client = gh(os.getenv('ghapitoken'))
        except Exception as e:
            self.logger.critical(f'Exception is {e}')
            raise(e)


def main():

    # handle logging
    log_filename = f'ci_long_'\
                   f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log'
    logging.basicConfig(filename=log_filename, filemode='w',
                        level=logging.INFO)
    logger = logging.getLogger('MAIN')
    logger.info('Starting Script')

    # setup interface with GitHub
    logger.info('Setting up GitHub interface.')
    ghinterface_obj = GHInterface()

    config = config_parser()

    # Read file that has info on uncompleted tests

    file_name = 'Longjob.cfg'
    if not os.path.exists(file_name):
        logger.info(f'Could not find {file_name}. Exiting.')
        quit()

    config.read(file_name)
    num_sections = len(config.sections())
    logger.info(f'Experiments running: {num_sections}')

    # Words to search for in log to signal success or failure
    complete_string = "This cycle is complete"
    failed_string = "DEAD"
    expt_done_count = 0

    pr_comment = ''
    for ci_log in config.sections():
        logger.info(f'{ci_log}: {config[ci_log]["pr_repo"]}')
        if os.path.exists(ci_log):
            expt_done = False
            expt = config[ci_log]["expt"]
            machine = config[ci_log]["machine"]
            pr_num = int(config[ci_log]["pr_num"])
            issue_id = int(config[ci_log]["issue_id"])
            repo = ghinterface_obj.client.get_repo(config[ci_log]["pr_repo"])
            pr = repo.get_pull(pr_num)
            with open(ci_log) as fname:
                for line in fname:
                    expt_string = ''
                    if complete_string in line:
                        expt_string = "Succeeded"
                    else:
                        if failed_string in line:
                            expt_string = "Failed"
                    if expt_string:
                        expt_done = True
                        newtext = f'Experiment {expt_string} '
                        pr_comment += f'{newtext}'
                        newtext = f'on {machine}: {expt}'
                        pr_comment += f'{newtext}\n'
                        if expt_string == "Failed":
                            newtext = f'{line.rstrip()}'
                            pr_comment += f'{newtext}\n'
                        logger.info(f'Experiment {expt_string}: {expt}')
            if expt_done:
                expt_done_count = expt_done_count + 1
                config.remove_section(ci_log)
    logger.info(f'Experiments Completed: {str(expt_done_count)}')

    if expt_done_count:
        issue_comm = pr.get_issue_comment(id=issue_id)
        issue_text = issue_comm.body
        if expt_done_count == num_sections:
            os.remove(file_name)
            pr_comment += 'All experiments completed\n'
        else:
            # Write out the file with completed experiments removed
            with open(file_name, 'w') as fname:
                config.write(fname)
        issue_comm.edit(issue_text + pr_comment)


if __name__ == '__main__':
    main()
