import os
import time
from datadog import initialize, api
from ddtrace import tracer

class Metrics:
    send_metrics = False
    
    @classmethod
    def init(cls):
        if "DATADOG_API_KEY" in os.environ and "DATADOG_APP_KEY" in os.environ and "HOST" in os.environ:
            Metrics.send_metrics = True
            initialize()
            api.Event.create(title="Backend start", text="", tags=["server:backend", f"host:{os.environ['HOST']}"], alert_type="info")
            if "DD_TRACE_AGENT_HOST" in os.environ and "DD_TRACE_AGENT_PORT" in os.environ:
                tracer.configure(
                    https=False,
                    hostname=os.environ["DD_TRACE_AGENT_HOST"],
                    port=os.environ["DD_TRACE_AGENT_PORT"],
                )
        else:
            print("Datadog not configured")

    @classmethod
    def send_metric(cls, metric_name, **kwargs):
        if Metrics.send_metrics:
            kwargs['tags'] = ["server:backend", f"host:{os.environ['HOST']}"] + kwargs.get('tags', [])
            kwargs['points'][0] = (int(time.time()) , kwargs['points'][0])
            api.Metric.send(metric=metric_name, **kwargs)

    @classmethod
    def send_event(cls, event_name, event_data, **kwargs):
        if Metrics.send_metrics:
            kwargs['tags'] = ["server:backend", f"host:{os.environ['HOST']}"] + kwargs.get('tags', [])
            api.Event.create(title=event_name, text=event_data, tags=kwargs['tags'], alert_type=kwargs.get('alert_type', "info"))
