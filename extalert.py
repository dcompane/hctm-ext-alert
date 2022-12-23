
# Basic imports
import json
import sys
import logging

# Importing Control-M Python Client
from ctm_python_client.core.workflow import *
from ctm_python_client.core.comm import *
from ctm_python_client.core.monitoring import Monitor
from aapi import *

# Importing functions
from extalert_functions import args2dict
from extalert_functions import parsing_args
from extalert_functions import init_dbg_log
from extalert_functions import dbg_assign_var

# https://pysnow.readthedocs.io/en/latest/full_examples/create.html
from pysnow import Client as snow_cli

# To write the log and output to files for attaching.
import tempfile
import os

# To see if we need to set initial debug. If not, can be set at tktvars,
#    but logging will not be as throrugh in the beginning. 
from dotenv import dotenv_values

args = sys.argv
#args = 'eventType: I id: 156508 server: IN01 fileName: test.sh runId: 09n0p severity: V status: 0 ' \
#    'time: 20221210011729 user: updateTime: message: Ended not OK runAs: MDI_MINISAP_AWS ' \
#    'subApplication: tma-lambda-snowflake application: tma-data-pipeline jobName: tma-sap ' \
#    'host: mdi-azure type: R closedByControlM: ticketNumber:1234  runNo: 00001 notes: some'

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
    dbg_logger.info('Opening tktvars.json')
    with open('tktvars.json') as config_data:
        config=json.load(config_data)
        dbg_logger.debug('Config file is ' + str(config))
except FileNotFoundError as e:
    dbg_logger.info('Failed opening tktvars.json')
    dbg_logger.info('Exception: No config file (tktvars.json) found.')
    dbg_logger.info(e)
    sys.exit(24)

# Convert Alert to dict using keywords.
alert = args2dict(args, keywords)
dbg_logger.info('params: ' + args)
dbg_logger.info('dict is ' + str(alert))

if (config['pgmvars']['crttickets'] == 'no'):
    dbg_logger.info ('*' * 20 + ' Alert not sent to ticketing system.')
    dbg_logger.info()
    sys.exit(1)

#Set debug mode. It will be shown in the log. DO NOT POLLUTE!
if (config['pgmvars']['debug'] == 'yes'):
    debug = True
    dbg_logger.setLevel(logging.DEBUG)
    dbg_logger.debug('Startup logging level adjusted to debug by Config File')

if (config['pgmvars']['addtkt2alert'] == 'yes'):
    addtkt2alert = True 
    dbg_logger.info ('Ticket ID will be added to the alert.')
else:
    addtkt2alert = False
    dbg_logger.info ('Ticket ID will NOT be added to the alert.')


if (config['pgmvars']['ctmattachlogs'] == 'yes'):
    ctmattachlogs = True
    dbg_logger.info ('Attaching log and output to the ticket.')
else:
    ctmattachlogs = False
    dbg_logger.info ('Log and output will NOT be attached to the ticket.')



# Ticket variables from tktvars.json
tkt_url = dbg_assign_var(config['tktvars']['tkturl'], 'Ticketing URL',dbg_logger)
tkt_rest_path = '/table/incident'
tkt_id_caller = config['tktvars']['tktsysidcaller']
tkt_attach_file=''
tkt_user = config['tktvars']['tktuser']
tkt_pass = config['tktvars']['tktpasswd']
#NewLine for SNOW messages
NL='\n';

# Load AAPI variables and create workflow object if need to attach logs
if ctmattachlogs:
    host_name=config['ctmvars']['ctmaapi']
    api_token=config['ctmvars']['ctmtoken']
    w = Workflow(Environment.create_saas(endpoint=host_name,api_key=api_token))

ctmweburl=config['ctmvars']['ctmweb']

# Other ticket variables that may be needed to add to tktvars (hardcoded here for simplicity)
#### Build Ticket fields
tkt_category=dbg_assign_var('Service Interruption', 'Ticket category', dbg_logger)
tkt_urgency=dbg_assign_var('1', 'Ticket Urgency', dbg_logger)
tkt_impact=dbg_assign_var('2', 'Ticket Impact', dbg_logger)
tkt_watch_list=dbg_assign_var('dcompane@gmail.com', 'Ticket watchlist (SNow specific', dbg_logger)
tkt_work_list=dbg_assign_var('dcompazrctm@gmail.com', 'Ticket worklist (SNow specific', dbg_logger)
tkt_assigned_group=dbg_assign_var('CTM GROUP', 'Ticket assigned group (SNow specific)', dbg_logger)
tkt_short_description=dbg_assign_var(f"{alert[keywords_json['jobName']]} {alert[keywords_json['message']]}",
                        'Ticket Short Description', dbg_logger)

# tkt_payload= {
#     'short_description': tkt_short_description,
#     'description': tkt_short_description,
# }
# If the alert is about a job
if(alert[keywords_json['runId']] != '00000'):
    job_log = \
        f"*" * 70 + NL + \
        f"Job log for {alert[keywords_json['jobName']]} OrderID: {alert[keywords_json['runId']]}" + NL+ \
        f"LOG includes all executions to this point (runcount: {alert[keywords_json['runNo']]}" + NL+ \
        f"NOTE: If ticket information is added to log, it is not shown here."+ NL+ \
        f"*" * 70 + NL

    job_output = \
        f"*" * 70 + NL + \
        f"" + NL+ \
        f"Job output for {alert[keywords_json['jobName']]} OrderID: {alert[keywords_json['runId']]}:" \
            f"{alert[keywords_json['runNo']]}" + NL+ \
        f"" + NL+ \
        f"*" * 70 + NL
        


    snow_client = snow_cli(instance=tkt_url, user=tkt_user, password=tkt_pass)
    snow_incidents = snow_client.resource(api_path=tkt_rest_path)

# get order date from status.orderDate. Status may return folders and jobs.
# for the job whose runId is the alert, get the order date
# "orderDate": "180903",
# https://stackoverflow.com/questions/7079241/python-get-a-dict-from-a-list-based-on-something-inside-the-dict

    # snow_payload= {'short_description': TKT_SHORT_DESCRIPTION,
    #     'assignment_group': TKT_ASSIGNED_GROUP,
    #     'urgency': TKT_URGENCY,
    #     'impact': TKT_IMPACT,
    #     'comments': TKT_COMMENTS, 
    #     'watch_list': TKT_WATCH_LIST, 
    #     'category': TKT_CATEGORY, 
    #     'caller_id': TKT_CALLER, 
    #     'work_notes': TKT_WORK_NOTES,
    #     'work_notes_list': TKT_WORK_LIST
    #     }

    snow_payload= {
        'short_description': tkt_short_description,
        'description': tkt_short_description,
        }
    # Create a new incident record
    result = snow_incidents.create(payload=snow_payload)

    snow_sys_id = result.__getitem__('sys_id')
    snow_incident_number =  result.__getitem__('number')

        # Load AAPI variables and create workflow object if need to attach logs
    if ctmattachlogs:
        incident = snow_incidents.get(query={'number': snow_incident_number})
        host_name=config['ctmvars']['ctmaapi']
        api_token=config['ctmvars']['ctmtoken']
        w = Workflow(Environment.create_saas(endpoint=host_name,api_key=api_token,))

        monitor = Monitor(aapiclient=w.aapiclient)
        #Check on this. is getting also folders.
        status = monitor.get_statuses(
                filter={"jobid": f"{alert[keywords_json['server']]}:{alert[keywords_json['runId']]}"})
        log = monitor.get_log(f"{alert[keywords_json['server']]}:{alert[keywords_json['runId']]}")

        # need to add code in case the output is not available
        #   Use status outputURI which should say there is no output.
        output = monitor.get_output(f"{alert[keywords_json['server']]}:{alert[keywords_json['runId']]}", 
                run_no=alert[keywords_json['runNo']])
        # Change \n to CRLF on log and output
        #    Log will always exist but output may not
        job_log = (job_log + NL + log)
        if output is not None :
            job_output = (job_output + NL +  output)
        else:
            job_output = (job_output + NL +  f"*" * 70 + NL + 
                        "NO OUTPUT AVAILABLE FOR THIS JOB" + NL + f"*" * 70 )
        file_log = f"log_{alert[keywords_json['runId']]}_{alert[keywords_json['runNo']]}.txt"
        file_output = f"output_{alert[keywords_json['runId']]}_{alert[keywords_json['runNo']]}.txt"

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







pass
