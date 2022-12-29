
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
    RETURN_VALUES = ["Incident Number", "Request ID"]
    incident, status_code = itsm_client.create_form_entry(itsm_form, itsm_payload, RETURN_VALUES)
    incident_id = incident["values"]["Incident Number"]
    request_id = incident["values"]["Request ID"]
    return incident_id, request_id

def attachFile(*args):
    pass
    return None

#########################################
# MAIN STARTS HERE
#########################################
assert __name__ != '__main__', 'Do not call me directly... This is existentially impossible!'