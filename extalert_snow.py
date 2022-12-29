
from pysnow import Client as snow_cli

# To write the log and output to files for attaching.
import tempfile
import os

def connTktClient(tkt_url: snow_cli, tkt_user, tkt_pass, logger):
    logger.debug('Connecting to Ticketing System')
    snow_client = snow_cli(instance=tkt_url, user=tkt_user, password=tkt_pass)
    return snow_client

def crtTkt (snow_client: snow_cli, tkt_rest_path, snow_payload, logger):
    logger.debug('Setting path for ticket creation')
    snow_incidents = snow_client.resource(api_path=tkt_rest_path)
    logger.debug('Creating incident record')
    result = snow_incidents.create(payload=snow_payload)
    snow_incident_number =  result.__getitem__('number')
    return snow_incident_number

def attachFile(snow_incidents, snow_incident_number, file_name, logger):
    logger.debug(f'Attaching file to incident {snow_incident_number}')
    incident = snow_incidents.get(query={'number': snow_incident_number})
    incident.upload(file_path=file_name)
    os.remove(file_name)
    return None

def buildPayload(alert, )

tkt_payload= {'short_description': tkt_short_description,
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