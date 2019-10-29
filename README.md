[Connexion](https://github.com/zalando/connexion) with benefits for microservices.

# Connexion Plus

If you want to use [Connexion](https://github.com/zalando/connexion) for your microservice, you have to add an [opentracing](https://opentracing.io/) or [prometheus](https://prometheus.io/) client on your own. With this library, you instantiate everything before your connexion app starts and this library will take care to put it all together, so you get everything fine.

If you want to know more about the used libraries, please go to the corresponding documentaries.

## Importing
```python
import connexion_plus
```

## OpenTracing

Currently, all opentracing implementation (e.g. [jaeger-client](https://pypi.org/project/jaeger-client/)) are supported for tracing. If you want to use it, you have to initialize the client before you start your connexion app and give it via the `tracer`-parameter to the `connexion_plus` Factory, where the magic happens.

The following example uses jaeger-client (`pip install jaeger-client`) implementation.

```python
import connexion_plus
from jaeger_client import Config as jConfig

config = jConfig(
        config={
            'logging': True,
        },
    )
jaeger_tracer = config.initialize_tracer()

app = connexion.App(__name__)
connexion_plus.Factory(app, tracer=jaeger_tracer)
```

## Prometheus

Currently, it is only the [prometheus-flask-exporter](https://pypi.org/project/prometheus-flask-exporter/) supported for connexion, so only for flask connexion. You only have to set the `metrics`-parameter to `True`

```python
import connexion_plus

app = connexion.App(__name__)
connexion_plus.Factory(app, metrics=True)
```

## Example

If you want to use `tracer` and `metrics` together, see here a complete example.

```python
import connexion_plus
from jaeger_client import Config as jConfig

config = jConfig(
        config={
            'logging': True,
        },
    )
jaeger_tracer = config.initialize_tracer()

app = connexion.App(__name__)
connexion_plus.Factory(app, tracer=jaeger_tracer, metrics=True)
```

If you add the line `metrics_factory=PrometheusMetricsFactory(namespace='yourAppName')` to your jaeger-client-config, you get the metrics out of jaeger to your flask app.

