[![PyPI version](https://badge.fury.io/py/connexion-plus.svg)](https://badge.fury.io/py/connexion-plus)

[Connexion](https://github.com/zalando/connexion) with benefits for microservices.

# Connexion Plus

If you want to use [Connexion](https://github.com/zalando/connexion) for your microservice, you have to add an [opentracing](https://opentracing.io/) or [prometheus](https://prometheus.io/) client on your own. With this library, you instantiate everything before your connexion app starts and this library will take care to put it all together, so you get everything fine.

This library give you a new class `App`, which you have to use instead of the connexion FlaskApp, to get everything working. The App inheritates from connexion app, so you can use it with your old code, but replace your import with `from connexion_plus import App`.

If you want to know more about the used libraries, please go to the corresponding documentaries.

## Dependencies

- [Connexion](https://github.com/zalando/connexion)
- [opentracing-python-instrumentation](https://github.com/uber-common/opentracing-python-instrumentation)
- [Flask-Opentracing](https://github.com/opentracing-contrib/python-flask)
- [jaeger-client](https://pypi.org/project/jaeger-client/)
- [requests](https://pypi.org/project/requests/)
- [prometheus-flask-exporter](https://pypi.org/project/prometheus-flask-exporter/)


## Importing
```python
from connexion_plus import App
```

## OpenTracing / Jaeger-Client

Currently, all opentracing implementation (e.g. [jaeger-client](https://pypi.org/project/jaeger-client/)) are supported for tracing. But this library use a third party function, that only supports Flask. If you want to use it, you have to initialize the client before you start your connexion app and give it via the `tracer`-parameter to the `connexion_plus` App, where the magic happens.

The following example uses jaeger-client (`pip install jaeger-client`) implementation.

```python
from connexion_plus import App
from jaeger_client import Config as jConfig

config = jConfig(
        config={
            'logging': True,
        },
    )
jaeger_tracer = config.initialize_tracer()

app = App(__name__, use_tracer=jaeger_tracer)
```

If you use the tracer, you get also a TracingHandler in your logging module under the empty name, so your logging message can be logged with opentracing.

```python
logging.getLogger('')
```

You can edit the logging-level with the `use_logging_level`-parameter of the addServices-method. DEBUG is the default level, so you get everything from the log within a route in your opentracing-ui. (As long as there are a span while you write a logging message, you will see the logging message in your span)
```python
import logging
from connexion_plus import App

app = App(app, use_tracer=config.initialize_tracer(), use_logging_level=logging.DEBUG)
```

It improve the performance slightly, when you set the log-level to a higher level (INFO, WARNING).

## Prometheus / Metrics

Currently, it is only the [prometheus-flask-exporter](https://pypi.org/project/prometheus-flask-exporter/) supported for connexion, so only for flask connexion. You only have to set the `metrics`-parameter to `True`

```python
from connexion_plus import App

app = App(__name__, use_metric=True)
```

## Complete example

If you want to use `tracer` and `metrics` together, see here a complete example. This currently works only with flask (see prometheus)

```python
from connexion_plus import App
from jaeger_client import Config as jConfig
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
import logging

config = jConfig(
        config={
            'logging': True,
        },
        # use this, if you want to track your tracing itself with prometheus
        metrics_factory = PrometheusMetricsFactory(namespace=name),
    )
jaeger_tracer = config.initialize_tracer()

app = App(__name__, use_tracer=jaeger_tracer, use_metric=True, use_logging_level=logging.DEBUG)
app.add_api('openapi.yaml', resolver=RestyResolver('api'))
```

If you add the line `metrics_factory=PrometheusMetricsFactory(namespace='yourAppName')` to your jaeger-client-config, you get the metrics out of jaeger into your flask app to track all metrics at once `/metrics`.

## More features

If you want to get the current tracing object in a request context, you can use [FlaskTracing](https://github.com/opentracing-contrib/python-flask#accessing-spans-manually)

```python
import Flasktracing
FlaskTracing.get_span(request)
```

If you get a collision of your view-functions, you can use from `from connexion-plus.MultipleResourceResolver import MultipleResourceResolver` as a replacement for RestyResolver to get better control of multi resource path e.g. /resource1/{id1}/resource2/{id2} tries to find the classes *Resource1Resource2* or *resource1resource2* in the given "api" folder.

## Examples

You can find more examples in the [repo](https://github.com/Heiss/connexion-plus/examples). *Tutorial1* is a simple small (without bonuscode) script without an openapi definition.

Please use *Tutorial2* if you want a complete usage example.

## Research data services

This library is under development for the project [research data services](http://research-data-services.info), a microservice ecosystem.
