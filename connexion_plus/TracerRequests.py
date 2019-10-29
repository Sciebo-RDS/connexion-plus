from requests import api
from .Util import get_tracer
import sys
from opentracing_instrumentation import request_context

def tracerRequestsDecorator(func, tracer):
    def wrapper(method, url, **kwargs):
        if 'header' not in kwargs:
            kwargs['header'] = {}
            
        span = request_context.get_current_span()
        tracer.inject(span, Format.HTTP_HEADERS, kwargs['header'])
        #func(*args, **kwargs)
        print("testitest")
        sys.exit(0)
        return func(*args, **kwargs)
        
    return wrapper

requests = api
requests.request = tracerRequestsDecorator(api.request, get_tracer())

print(requests.get("http://google.de").request.headers)
sys.exit(0)

