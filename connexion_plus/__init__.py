name = "connexion-plus"

from .Factory import Factory

from opentracing_instrumentation.client_hooks import install_all_patches
# Automatically trace all requests made with 'requests' library.
install_all_patches()

