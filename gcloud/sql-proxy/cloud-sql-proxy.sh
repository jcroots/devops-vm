#!/bin/bash
set -eu

env_filename=/usr/local/etc/deploy-vm.environment
if test -s "${env_filename}"; then
	# shellcheck disable=SC1090
	source "${env_filename}"
fi

db_connection=${DATABASE_CONNECTION:-db_connection:not:set}

# just to check we can execute it
/usr/local/bin/cloud_sql_proxy --version

exec /usr/local/bin/cloud_sql_proxy --credentials-file /usr/local/secrets/credentials/sql-client-sa.json "${db_connection}"
