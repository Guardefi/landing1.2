import sys, types

metrics_stub = types.ModuleType("utils.metrics")
class PerformanceMonitor:
    def __init__(self, *args, **kwargs):
        pass
    def record(self, *args, **kwargs):
        pass

metrics_stub.PerformanceMonitor = PerformanceMonitor
sys.modules.setdefault("utils.metrics", metrics_stub)
