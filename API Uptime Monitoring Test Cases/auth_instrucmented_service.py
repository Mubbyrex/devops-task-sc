from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Initialize OTEL with resource info
resource = Resource.create({
    "service.name": "auth-service",
    "service.version": "1.0.0",
    "deployment.environment": "production"
})

# Set up tracing
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Set up metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter()
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Create metrics
auth_requests = meter.create_counter(
    "auth.requests",
    description="Number of authentication requests"
)
token_duration = meter.create_histogram(
    "auth.token_issuance_duration",
    description="Time taken to issue tokens",
    unit="ms",
)

class AuthService:
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
    
    async def authenticate_user(self, username, password):
        with self.tracer.start_as_current_span("authenticate_user") as span:
            span.set_attribute("user.name", username)
            
            # Record the authentication attempt
            auth_requests.add(1, {"method": "password"})
            
            with token_duration.record_duration():
                # Your existing authentication logic here
                result = await self._verify_credentials(username, password)
                span.set_attribute("auth.success", result)
                return result
    
    async def _verify_credentials(self, username, password):
        with self.tracer.start_as_current_span("verify_credentials") as span:
            # Simulate credential verification
            return True
