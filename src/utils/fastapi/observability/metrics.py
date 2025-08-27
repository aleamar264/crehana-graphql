"""The metrics and dashboards are inspired in the repository from
https://github.com/blueswen/fastapi-observability/blob/main/fastapi_app/utils.py"""

from collections.abc import Callable

from fastapi import FastAPI, Request
from prometheus_client import Counter, Gauge
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info
from pydantic import BaseModel
from starlette.routing import Match


class PrometheusMetrics(BaseModel):

    app_name: str

    def fastapi_responses_total(self) -> Callable[[Info], None]:
        METRIC = Counter(
            "fastapi_responses_total",
            "Total count of responses by method, path and status codes.",
            labelnames=(
                "method",
                "path",
                "status_code",
                "app_name",
            ),
        )
        INFO = Gauge("fastapi_app_info", "FastAPI application information.", ["app_name"])
        INFO.labels(app_name=self.app_name).inc()

        def instrumentation(info: Info) -> None:
            method = info.request.method
            path, is_handled_path = self.get_path(info.request)
            status_code = info.response.status_code
            METRIC.labels(
                method=method, path=path, app_name=self.app_name, status_code=status_code
            ).inc()

        return instrumentation


    def get_path(self, request: Request) -> tuple[str, bool]:
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True

        return request.url.path, False

    def init_instrumentation(self, app: FastAPI):

        instrumentator = Instrumentator(
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/metrics"],
            env_var_name="APP_ENV",
            should_ignore_untemplated=True,
        )

        # Request metrics
        instrumentator.add(
            metrics.request_size(
                metric_name="http_request_size_bytes",
                should_include_handler=True,
                should_include_method=True,
            )
        ).add(
            metrics.response_size(
                metric_name="http_response_size_bytes",
                should_include_handler=True,
            )
        ).add(
            metrics.latency(
                metric_name="http_request_duration_seconds",
                should_include_handler=True,
                should_include_method=True,
            )
        ).add(
            metrics.latency(
                metric_name="http_request_duration_highr_seconds",
                buckets=[
                    0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5,
                    10.0, 25.0, 50.0, 75.0, 100.0, float("inf")
                ],
            )
        ).add(self.fastapi_responses_total())

        return instrumentator.instrument(app=app)


