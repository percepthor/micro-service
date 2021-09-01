import sys
import ctypes

from cerver import *
from cerver.http import *

from config import *

from routes.service import *

micro_service = None

# end
def end (signum, frame):
	# cerver_stats_print (micro_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (micro_service))
	cerver_teardown (micro_service)
	cerver_end ()

	sys.exit ("Done!")

def service_set_routes (http_cerver):
	# register top level route
	# GET /api/service
	main_route = http_route_create (REQUEST_METHOD_GET, b"api/service", main_handler)
	http_cerver_route_register (http_cerver, main_route)

	# GET /api/service/version
	version_route = http_route_create (REQUEST_METHOD_GET, b"version", version_handler)
	http_route_child_add (main_route, version_route)

def start ():
	global micro_service
	micro_service = cerver_create_web (
		b"micro-service", PORT, CERVER_CONNECTION_QUEUE
	)

	# main configuration
	cerver_set_alias (micro_service, b"service")

	cerver_set_receive_buffer_size (micro_service, CERVER_RECEIVE_BUFFER_SIZE)
	cerver_set_thpool_n_threads (micro_service, CERVER_TH_THREADS)
	cerver_set_handler_type (micro_service, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (micro_service, True)

	# HTTP configuration
	http_cerver = http_cerver_get (micro_service)

	service_set_routes (http_cerver)

	# add a catch all route
	http_cerver_set_catch_all_route (http_cerver, service_catch_all_handler)

	# admin
	http_cerver_enable_admin_routes (http_cerver, True)

	# start
	cerver_start (micro_service)
