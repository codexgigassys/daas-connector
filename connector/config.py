# --- Connection configuration ---
PROTOCOL = 'http'

IP = '138.197.102.77'

PORT = 443


# --- Credentials configuration ---
""" You can set either the token or username + password. """
TOKEN = ''

USERNAME = 'codex'

PASSWORD = 'codexcodex'


# --- Callback configuration ---
CALLBACK_URL = ''

# This variable should point to a function able to save requirement information to codex database and create a new
# task to reprocess the given sample
PROCESS_CALLBACK_FUNCTION = lambda sample_sha1, is_decompilable, daas_sample_id: None
