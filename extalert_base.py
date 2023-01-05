
# Basic imports
import json
import sys
import logging

from importlib import import_module

# Importing Control-M Python Client
from ctm_python_client.core.workflow import *
from ctm_python_client.core.comm import *
from ctm_python_client.core.monitoring import Monitor
from aapi import *

# Importing functions
from extalert_functions import *
from extalert_BHITSM import *
from extalert_snow import *


# To see if we need to set initial debug. If not, can be set at tktvars,
#    but logging will not be as throrugh in the beginning. 
# need to pip install  python-dotenv
from dotenv import dotenv_values

class tkt_data:
    def __init__(self, config) -> None:
        tkt_sol = dbg_assign_var(f"{config['pgmvars']['ticket_sol']}vars", 'Ticketing Solution used',dbg_logger)
        
        self.tkt_url         = dbg_assign_var(config[tkt_sol]['tkturl'], 'Ticketing URL',dbg_logger)
        self.tkt_rest_path   = dbg_assign_var(config[tkt_sol]['tktpath'],'',dbg_logger)
        self.tkt_user        = dbg_assign_var(config[tkt_sol]['tktuser'],'',dbg_logger)
        self.tkt_pass        = dbg_assign_var(config[tkt_sol]['tktpasswd'],'',dbg_logger)
        self.tkt_verify_ssl  = dbg_assign_var(True if config[tkt_solution]['verifySSL'] == 'yes' else False, 'Verify SSL on REST request', dbg_logger)
        self.tkt_category    = dbg_assign_var('Service Interruption', 'Ticket category', dbg_logger)
        self.tkt_urgency     = dbg_assign_var('1', 'Ticket Urgency', dbg_logger)
        self.tkt_impact      = dbg_assign_var('2', 'Ticket Impact', dbg_logger)
        self.tkt_assigned_group = dbg_assign_var('CTM GROUP', 'Ticket assigned group (SNow specific)', dbg_logger)
        self.tkt_short_description = dbg_assign_var(f"{alert[keywords_json['jobName']]}-{alert[keywords_json['message']]}",
                                'Ticket Short Description', dbg_logger)

        # Solution specific variables
        if tkt_sol.split('vars')[0] == 'BHITSM':
            self.tkt_verify_ssl  = dbg_assign_var(True if config[tkt_solution]['verifySSL'] == 'yes' else False, 'Verify SSL on REST request', dbg_logger)
            
        elif tkt_sol.split('vars')[0] == 'SNOW':
            self.tkt_id_caller   = dbg_assign_var(config[tkt_sol]['tktsysidcaller'],'',dbg_logger)
            self.tkt_watch_list  = dbg_assign_var('emailofwatch@somedomain.com', 'Ticket watchlist (SNow specific)', dbg_logger)
            self.tkt_work_list   = dbg_assign_var('emailofwork@somedomain.com', 'Ticket worklist (SNow specific)', dbg_logger)


        
# Set exit code for the procedure
exitrc = 0

# Initialize logging
dbg_logger=init_dbg_log()

try:
    config = dotenv_values('.env.debug')  # could render config = {"DEBUG": "true"}
    dbg_logger.info(f'file ".env.debug" was loaded. Setting debug to {config["DEBUG"]}.')
except:
    dbg_logger.info('file ".env.debug" is not available. Setting debug to False.')
    config = {}
    config['DEBUG'] = 'false'

# Setting logging level according to .env
if config['DEBUG'] == 'true':
    dbg_logger.setLevel(logging.DEBUG)
    dbg_logger.info('Startup logging to file level adjusted to debug (verbose)')

try:
    dbg_logger.info('Opening field_names.json')
    with open('field_names.json') as keyword_data:
        json_keywords = json.load(keyword_data)
        dbg_logger.debug('Fields file is ' + str(json_keywords))
        keywords = []
        keywords_json = {}
        for i in range(len(json_keywords['fields'])):
            element=[*json_keywords['fields'][i].values()]
            keywords.append(element[0]+':')
            keywords_json.update(json_keywords['fields'][i])
except FileNotFoundError as e:
    # Template file with fields not found
    # Assuming all fields will be passed in standard order
    dbg_logger.info('Failed opening field_names.json. Using default')
    keywords_json = dbg_assign_var( { {'eventType': 'eventType'}, {'id': 'alert_id'}, {'server': 'server'}, 
                    {'fileName': 'fileName'}, {'runId': 'runId'}, {'severity': 'severity'}, 
                    {'status': 'status'}, {'time': 'time'}, {'user': 'user'}, {'updateTime': 'updateTime'},
                    {'message': 'message'}, {'runAs': 'runAs'}, {'subApplication': 'subApplication'},
                    {'application': 'application'}, {'jobName': 'jobName'}, {'host': 'host'}, {'type': 'type'},
                    {'closedByControlM': 'closedByControlM'}, {'ticketNumber': 'ticketNumber'}, {'runNo': 'runNo'}, 
                    {'notes': 'notes'} }, "Default field names used internally", dbg_logger)
    keywords = dbg_assign_var(['eventType:', 'id:', 'server:', 'fileName:', 'runId:', 'severity:', 'status:',
            'time:', 'user:' ,'updateTime:' ,'message: ' ,'runAs:' ,'subApplication:' ,'application:', 
            'jobName:', 'host:', 'type:', 'closedByControlM:', 'ticketNumber:', 'runNo:', 'notes:'], 
            'Default field names assigned.', dbg_logger)

try:
    dbg_logger.info('Opening tktvars_dco.json')
    with open('tktvars_dco.json') as config_data:
        config.update(json.load(config_data))
        dbg_logger.debug('Config file is ' + str(config_data))
except FileNotFoundError as e:
    dbg_logger.critical('Failed opening tktvars.json')
    dbg_logger.critical('Exception: No config file (tktvars.json) found.')
    dbg_logger.critical(e)
    sys.exit(24)


if (config['pgmvars']['crttickets'] == 'no'):
    dbg_logger.info ('*' * 20 + ' Alert not sent to ticketing system.')
    dbg_logger.info()
    exitrc = 12
    sys.exit(exitrc)

#Set debug mode. It will be shown in the log. DO NOT POLLUTE!
if (config['pgmvars']['debug'] == 'yes'):
    debug = True
    dbg_logger.setLevel(logging.DEBUG)
    dbg_logger.debug('Startup logging level adjusted to debug by Config File')

if (config['pgmvars']['ctmattachlogs'] == 'yes'):
    ctmattachlogs = True
    dbg_logger.info ('Log and output will be attached to the ticket.')
else:
    ctmattachlogs = False
    dbg_logger.info ('Log and output will NOT be attached to the ticket.')

if (config['pgmvars']['addtkt2alert'] == 'yes'):
    addtkt2alert = True 
    dbg_logger.info ('Ticket ID will be added to the alert.')
else:
    addtkt2alert = False
    dbg_logger.info ('Ticket ID will NOT be added to the alert.')

# This is not implemented. Should not be set to 'yes'
if (config['pgmvars']['ctmupdatetkt'] == 'yes'):
    ctmupdatetkt = True
    dbg_logger.info ('Updates will be sent to the system.')
else:
    ctmupdatetkt = False
    dbg_logger.info ('Updates will NOT be sent to the system.')


tktvars=tkt_data(config)
tkt_sol = dbg_assign_var(config['pgmvars']['ticket_sol'].split('vars')[0], "Solution in effect is ", dbg_logger)

try:
    import_module(f'extalert_{tkt_sol}')
except (e):
    dbg_logger.critical(f"Module for {tkt_sol} has not been coded.")
    raise (e)

# Load ctmvars
#   Set AAPI variables and create workflow object
host_name = config['ctmvars']['ctmaapi']
api_token = config['ctmvars']['ctmtoken']
#   Set host for web url
ctmweb=config['ctmvars']['ctmweb']
ctm_is_helix = True if config['ctmvars']['ctmplatform'] == "Helix" else False

# Connect to ticketing
tktconn = connTktClient(tktvars.tkt_url, tktvars.tkt_user, tktvars.tkt_pass, dbg_logger)

# Evaluate alert and convert args to list
args = ''.join(map(lambda x: str(x)+' ', sys.argv[1:]))
# Convert Alert to dict using keywords.
alert = args2dict(args, keywords)
dbg_logger.debug('params: ' + args)
dbg_logger.debug('dict is ' + str(alert))

# Exit if alert should not be sent.
if ctmupdatetkt and (alert[keywords_json['eventType']] != "I"):
    exitrc = 24
    sys.exit(exitrc)

# Configure Helix Control-M AAPI client
monitor = ctmConnAAPI(host_name, api_token, dbg_logger)

# If the alert is about a job
alert_is_job = False
output_file = None
log_file = None
if alert[keywords_json['runId']] != '00000':
    dbg_logger.debug("Alert is job alert.")
    alert_is_job = True
    status = dbg_assign_var(monitor.get_statuses(
            filter={"jobid": f"{alert[keywords_json['server']]}:{alert[keywords_json['runId']]}"}), 
            "Status of job", dbg_logger)

    buildPayload(alert, config, alert_is_job, status, logger)

    output = ctmOutputFile(monitor,alert[keywords_json['jobName']], 
                alert[keywords_json['server']],alert[keywords_json['runId']],
                alert[keywords_json['runNo']], dbg_logger)
    out_name = f"output_{alert[keywords_json['runId']]}_{alert[keywords_json['runNo']]}.txt"

    output_file = writeFile4Attach(out_name, output, '', dbg_logger)

    log = ctmOutputFile(monitor,alert[keywords_json['jobName']], 
                alert[keywords_json['server']],alert[keywords_json['runId']],
                alert[keywords_json['runNo']], dbg_logger)
    log_name = f"output_{alert[keywords_json['runId']]}_{alert[keywords_json['runNo']]}.txt"

    log_file = writeFile4Attach(out_name, output, '', dbg_logger)

else:
    dbg_logger.info("Alert is NOT job alert.")
    alert_is_job = False




    # Create a new incident record
result = snow_incidents.create(payload=snow_payload)

snow_sys_id = result.__getitem__('sys_id')
snow_incident_number =  result.__getitem__('number')

# Load AAPI variables and create workflow object if need to attach logs
if ctmattachlogs and alert_is_job:
    incident = snow_incidents.get(query={'number': snow_incident_number})
    log = dbg_assign_var(monitor.get_log(f"{alert[keywords_json['server']]}:{alert[keywords_json['runId']]}"), "Log of Job", dbg_logger)

    # need to add code in case the output is not available
    #   Use status outputURI which should say there is no output.
    output = dbg_assign_var(monitor.get_output(f"{alert[keywords_json['server']]}:{alert[keywords_json['runId']]}", 
            run_no=alert[keywords_json['runNo']]), "Output of job", dbg_logger)
    # Change \n to CRLF on log and output
    #    Log will always exist but output may not
    job_log = (job_log + '\n' + log)
    if output is not None :
        job_output = (job_output + '\n' +  output)
    else:
        job_output = (job_output + '\n' +  f"*" * 70 + '\n' + 
                    "NO OUTPUT AVAILABLE FOR THIS JOB" + '\n' + f"*" * 70 )
    file_log = f"log_{alert[keywords_json['runId']]}_{alert[keywords_json['runNo']]}.txt"
    file_output = f"output_{alert[keywords_json['runId']]}_{alert[keywords_json['runNo']]}.txt"

    # Write log
    # Declare object to open temporary file for writing
    tmpdir = tempfile.gettempdir()
    file_name =tmpdir+os.sep+file_log
    fh = open(file_name,'w')
    # content = job_log.replace('\n', '\r\n')
    content = job_log
    try:
        # Print message before writing
        dbg_logger.debug(f'Write data to log file {file_name}')
        # Write data to the temporary file
        fh.write(content)
        # Close the file after writing
        fh.close()
        # Attach to Incident
        incident.upload(file_path=file_name)
    finally:
        # Print a message before reading
        dbg_logger.debug("log data added to the ticket")
        
    os.remove(file_name)

    # Write output
    # Declare object to open temporary file for writing
    tmpdir = tempfile.gettempdir()
    file_name =tmpdir+os.sep+file_output
    fh = open(file_name,'w')
    # content = job_output.replace('\n', '\r\n')
    content = job_output
    try:
        # Print message before writing
        dbg_logger.debug(f'Write data to output file {file_name}')
        # Write data to the temporary file
        fh.write(content)
        # Close the file after writing
        fh.close()
        # Attach to Incident
        incident.upload(file_path=file_name)
    finally:
        # Print a message before reading
        dbg_logger.debug("output data added to the ticket")
        
    os.remove(file_name)

sys.exit(exitrc)