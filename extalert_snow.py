
from pysnow import Client as snow_cli

# To write the log and output to files for attaching.
import tempfile
import os

def connTktClient(tkt_url: snow_cli, tkt_user, tkt_pass, output, log, logger):
    logger.debug('Connecting to Ticketing System')
    snow_client = snow_cli(instance=tkt_url, user=tkt_user, password=tkt_pass)
    return snow_client

def crtTkt (snow_client: snow_cli, tkt_rest_path, snow_payload, logger):
    logger.debug('Setting path for ticket creation')
    snow_incidents = snow_client.resource(api_path=tkt_rest_path)
    logger.debug('Creating incident record')
    result = snow_incidents.create(payload=snow_payload)
    snow_incident_number =  result.__getitem__('number')
    incident = snow_incidents.get(query={'number': snow_incident_number})

    if output is not None:
        attachFile(snow_incident, snow_incident_number, output, logger)
    if log is not None:
        attachFile(snow_incident, snow_incident_number, log, logger)

    return snow_incident_number

def attachFile(snow_incident, snow_incident_number, file_name, logger):
    logger.debug(f'Attaching file to incident {snow_incident_number}')
    incident.upload(file_path=file_name)
    os.remove(file_name)
    return None

def buildPayload(alert, config, is_job, status, logger):

    tkt_category=dbg_assign_var('Service Interruption', 'Ticket category', dbg_logger)
    tkt_urgency=dbg_assign_var('1', 'Ticket Urgency', dbg_logger)
    tkt_impact=dbg_assign_var('2', 'Ticket Impact', dbg_logger)
    tkt_watch_list=dbg_assign_var('dcompane@gmail.com', 'Ticket watchlist (SNow specific', dbg_logger)
    tkt_work_list=dbg_assign_var('dcompazrctm@gmail.com', 'Ticket worklist (SNow specific', dbg_logger)
    tkt_assigned_group=dbg_assign_var('CTM GROUP', 'Ticket assigned group (SNow specific)', dbg_logger)
    tkt_short_description=dbg_assign_var(f"{alert[keywords_json['jobName']]} {alert[keywords_json['message']]}",
                            'Ticket Short Description', dbg_logger)

# If the alert is about a job
alert_is_job = False
if(alert[keywords_json['runId']] != '00000'):
    alert_is_job = True
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

    tkt_comments =  \
                f"Agent Name                  : {alert[keywords_json['host']]} {NL}" + \
                f"Folder Name                 : {status.statuses[0].folder} {NL}" + \
                f"Job Name                    : {alert[keywords_json['jobName']]} {NL}" + \
                f"Order ID                    : {alert[keywords_json['runId']]} {NL}" + \
                f"Run number                  : {alert[keywords_json['runNo']]} {NL}" + \
                f"Order Date                  : {status.statuses[0].order_date} {NL} {NL}" + \
                f"Ticket Notes                : {alert[keywords_json['notes']]} {NL} {NL}" + \
                f"Job Output and Log are attached  {NL} {NL}" + \
                f"The job can be seen on the {'Helix' if ctm_is_helix else ''} " + \
                f"Control-M Self Service site. Click the link below. {NL}" + \
                f"{NL}" + \
                f"https://{ctmweb}/ControlM/#Neighborhood:id={alert[keywords_json['runId']]}&ctm={alert[keywords_json['server']]}&name={alert[keywords_json['jobName']]}"+ \
                f"&date={status.statuses[0].order_date}&direction=3&radius=3" + \
                f"{NL}{NL}" if alert_is_job else "This alert is not job related"

    tkt_work_notes = f"Ticket created automatically by {'Helix' if ctm_is_helix else ''} Control-M" + \
        (f" for {alert[keywords_json['server']]}:{alert[keywords_json['runId']]}::{alert[keywords_json['runNo']]}" if alert_is_job else "")

    snow_payload= {'short_description': tkt_short_description,
        'assignment_group': tkt_assigned_group,
        'urgency': tkt_urgency,
        'impact': tkt_impact,
        'comments': tkt_comments, 
        'watch_list': tkt_watch_list, 
        'category': tkt_category, 
        'caller_id': tkt_id_caller, 
        'work_notes': tkt_work_notes,
        'work_notes_list': tkt_work_list
        }



    tkt_payload= {
        'short_description': tkt_short_description,
        'assignment_group': tkt_assigned_group,
        'urgency': tkt_urgency,
        'impact': tkt_impact,
        'comments': tkt_comments, 
        'watch_list': tkt_watch_list, 
        'category': tkt_category, 
        'caller_id': tkt_id_caller, 
        'work_notes': tkt_work_notes,
        'work_notes_list': tkt_work_list
        }




#########################################
# MAIN STARTS HERE
#########################################
assert __name__ != '__main__', 'Do not call me directly... This is existentially impossible!'