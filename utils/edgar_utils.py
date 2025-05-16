from edgar import *
from pyheaven import *
SEC_identity = LoadJson("SEC_identity.json")
SEC_name, SEC_email = SEC_identity['name'], SEC_identity['email']
set_identity(f"{SEC_name} {SEC_email}")
use_local_storage(True)
