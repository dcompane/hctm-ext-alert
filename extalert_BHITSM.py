
from remedy_py.RemedyAPIClient import RemedyClient as itsm_cli

# To write the log and output to files for attaching.
import tempfile
import os

def connTktClient(tkt_url, tkt_user, tkt_pass, logger):
    logger.debug('Connecting to Ticketing System')
    itsm_client = itsm_cli(tkt_url, tkt_user, tkt_pass, verify=True)
    return itsm_client


def crtTkt (itsm_client: itsm_cli, itsm_form, itsm_payload, logger):
    logger.debug('Creating incident record')
    # Create a new incident record
    RETURN_VALUES = ["Incident Number"]
    incident, status_code = itsm_client.create_form_entry(itsm_form, itsm_payload, RETURN_VALUES)
    incident_id = incident["values"]["Incident Number"]
    return incident_id, None

def attachFile(*args):
    pass
    return None

def buildPayload(alert, config, is_job, status, logger):

    #### Build Ticket fields
    tkt_urgency=dbg_assign_var('1-Critical', 'Ticket Urgency', dbg_logger)
    tkt_impact=dbg_assign_var('1-Extensive/Widespread', 'Ticket Impact', dbg_logger)
    tkt_short_description=dbg_assign_var((f"{alert[keywords_json['jobName']]} " if is_job else "") + 
          f"{alert[keywords_json['message']]}",'Ticket Short Description', dbg_logger)

    if is_job:
        ctmweb=config['ctmvars']['ctmweb']
        tkt_category=dbg_assign_var('User Service Restoration', 'Service Type', dbg_logger)
    
        tkt_comments =  \
            f"Agent Name                  : {alert[keywords_json['host']]} \n" + \
            f"Folder Name                 : {status.statuses[0].folder} \n" + \
            f"Job Name                    : {alert[keywords_json['jobName']]} \n" + \
            f"Order ID                    : {alert[keywords_json['runId']]} \n" + \
            f"Run number                  : {alert[keywords_json['runNo']]} \n" + \
            f"Order Date                  : {status.statuses[0].order_date} \n \n" + \
            f"Ticket Notes                : {alert[keywords_json['notes']]} \n \n" + \
            f"Job Output and Log are attached  \n \n" + \
            f"The job can be seen on the {'Helix' if ctm_is_helix else ''} " + \
            f"Control-M Self Service site. Click the link below. \n" + \
            f"\n" + \
            (f"https://{ctmweb}/ControlM/#Neighborhood:id={alert[keywords_json['runId']]}&ctm={alert[keywords_json['server']]}&name={alert[keywords_json['jobName']]}"+ \
            f"&date={status.statuses[0].order_date}&direction=3&radius=3" \
            if alert_is_job else "This alert is not job related") + "\n\n" + \
            f"Ticket created automatically by {'Helix' if ctm_is_helix else ''} Control-M" + \
            f" for {alert[keywords_json['server']]}:{alert[keywords_json['runId']]}::{alert[keywords_json['runNo']]}"
    
    else:
        tkt_category=dbg_assign_var('Infrastructure Service Restoration', 'Service Type', dbg_logger)
        tkt_comments = \
            f"Agent Name                  : {alert[keywords_json['host']]} \n" + \
            f"Order Date                  : {status.statuses[0].order_date} \n \n" + \
            f"Ticket Notes                : {alert[keywords_json['notes']]} \n \n" + \
            f"Ticket created automatically by {'Helix' if ctm_is_helix else ''} Control-M"


    payload = {
        "First_Name": "Helix Control-M",
        "Last_Name": "Account",
        "Description": tkt_short_description,
        "Impact": tkt_impact,
        "Urgency": tkt_urgency,
        "Status": "Assigned",
        "Reported Source": "Direct Input",
        "Service_Type": tkt_category,
        "z1D_Action": "CREATE",
        "Detailed_Description": tkt_comments
    }

    return payload

#########################################
# MAIN STARTS HERE
#########################################
assert __name__ != '__main__', 'Do not call me directly... This is existentially impossible!'