from connexion_plus import App
from connexion.resolver import RestyResolver
from jaeger_client import Config as jConfig
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
import logging

config = jConfig(
        config={
            'logging': True,
        },
        # use this, if you want to track your tracing itself with prometheus
        metrics_factory = PrometheusMetricsFactory(namespace=__name__),
    )
jaeger_tracer = config.initialize_tracer()

app = App(__name__, use_tracer=jaeger_tracer, use_metric=True, use_logging_level=logging.DEBUG)
app.add_api('openapi.yaml', resolver=RestyResolver('api'))

app.run(port=8080, server='gevent')

