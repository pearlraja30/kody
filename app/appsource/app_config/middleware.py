import uuid
import threading
from django.utils.deprecation import MiddlewareMixin

# Thread-local storage for tracing metadata
_thread_locals = threading.local()

def get_current_trace_id():
    return getattr(_thread_locals, 'traceid', 'N/A')

def get_current_span_id():
    return getattr(_thread_locals, 'spanid', 'N/A')

class TracingMiddleware(MiddlewareMixin):
    """
    Middleware to generate and inject traceid/spanid into the request lifecycle.
    """
    def process_request(self, request):
        # Generate new trace/span for this request
        _thread_locals.traceid = uuid.uuid4().hex[:8].upper()
        _thread_locals.spanid = uuid.uuid4().hex[:4].upper()
        
        # Optionally attach to request for template usage
        request.traceid = _thread_locals.traceid
        request.spanid = _thread_locals.spanid

    def process_response(self, request, response):
        # Clean up to prevent leakage
        if hasattr(_thread_locals, 'traceid'):
            del _thread_locals.traceid
        if hasattr(_thread_locals, 'spanid'):
            del _thread_locals.spanid
        return response
