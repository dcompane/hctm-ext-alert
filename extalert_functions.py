#########################################
# Evaluating make Python dict from CTM Alerts
#########################################
import re
def args2dict(tosplit, keys):
    def getkey(ls):
        for i in ls:
            if i is not None:
                return i.strip().rstrip(':')

    pattern = '|'.join(['(' + i + ')' for i in keys])
    lst = re.split(pattern, tosplit)

    lk = len(keys)
    elts = [((lst[i: i+lk]), lst[i+lk]) for i in range(1, len(lst), lk+1)]
    resul = {getkey(i): j.strip() for i,j in elts}
    return resul

#########################################
# Parsing arguments
#########################################
import argparse
def parsing_args():
    parser = argparse.ArgumentParser()
    #parser.add_argument('--action', '-a', dest='action', help='Type of action to perform',
    #                    choices=['list', 'fetch'])
    #parser.add_argument('--month', '-m', dest='month', help='Month of the report',
    #                    choices=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
    #                             'October', 'November', 'December'])
    #parser.add_argument('-y', '--year', dest='year', action='store', help='Year of report in the format of YYYY')
    #parser.add_argument('-v', '--verbose', help='Running with debug messages', action='store_true')
    #parser.add_argument('alert', metavar='N', type=str, nargs='+', help='fromScript')
    #params = parser.parse_args()
    #return params

#########################################
# Initialize logging for debug purposes
#########################################
# General logging settings
# next line is in case urllib3 (used with url calls) issues retry or other warnings.
def init_dbg_log():
    import logging
    from logging import handlers
    from os import path, getcwd
    from sys import stdout
    logging.captureWarnings(True)

    # Define dbg_logger
    dbg_logger = logging.getLogger('__SendTickets__', )
    # Logging format string
    # dbg_format_str = '[%(asctime)s] - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
    dbg_format_str = '[%(asctime)s] - %(levelname)s - %(message)s'
    dbg_format = logging.Formatter(dbg_format_str)
    # logging to file settings
    base_dir = getcwd() + path.sep
    dbg_filename = base_dir + 'autoalert.log'
    dbg_file = logging.handlers.RotatingFileHandler(filename=dbg_filename, mode='a', maxBytes=1000000, backupCount=10,
                                                    encoding=None, delay=False)
    # dbg_file.setLevel(logging.INFO)
    dbg_file.setFormatter(dbg_format)

    # Logging to console settings
    dbg_console = logging.StreamHandler(stdout)
    # Debug to console is always INFO
    dbg_console.setLevel(logging.INFO)
    dbg_console.setFormatter(dbg_format)

    # General logging settings
    # dbg_logger.setLevel(logging.DEBUG)
    dbg_logger.addHandler(dbg_file)
    dbg_logger.addHandler(dbg_console)

    # Heading of new logging session
    # Default logging level
    dbg_logger.setLevel(logging.INFO)
    dbg_logger.info('*' * 50)
    dbg_logger.info('*' * 50)
    dbg_logger.info('Startup Log setting established')
    return dbg_logger

#########################################
# Write DBG info on assigning variable
#########################################
def dbg_assign_var(to_assign, what_is_this,logger):
    logger.debug (f'{what_is_this}: {to_assign}')
    return to_assign


assert __name__ != '__main__', 'Do not call me directly... This is existentially impossible!'