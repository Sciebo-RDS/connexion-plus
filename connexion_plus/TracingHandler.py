from logging import StreamHandler

class TracingHandler(StreamHandler):
    def __init__(self, use_tracer):
        StreamHandler.__init__(self)
        self.tracer = use_tracer

    def emit(self, record):
        from opentracing_instrumentation import request_context
        span = request_context.get_current_span()
        
        if span is not None:
            msg = self.format(record)
            span.log_kv({"event": msg})

