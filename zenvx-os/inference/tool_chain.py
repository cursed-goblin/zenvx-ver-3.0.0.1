"""tool_chain.py - sequential tool execution with abort-on-failure."""


class ToolStep:
    def __init__(self, name, func, params=None, condition=None):
        self.name = name
        self.func = func
        self.params = params or {}
        self.condition = condition


class ToolChainResult:
    def __init__(self, success, results, failed_step=None):
        self.success = success
        self.results = results
        self.failed_step = failed_step


class ToolChain:
    def __init__(self, steps=None):
        self.steps = steps or []

    def add(self, step):
        self.steps.append(step)
        return self

    def run(self, initial=None):
        results = []
        prev = initial
        for step in self.steps:
            if step.condition and not step.condition(prev):
                continue
            try:
                prev = step.func(prev, **step.params)
                results.append((step.name, prev))
            except Exception as exc:  # noqa: BLE001
                results.append((step.name, f"ERROR: {exc}"))
                return ToolChainResult(False, results, failed_step=step.name)
        return ToolChainResult(True, results)

    @classmethod
    def ecommerce_buy(cls, search_fn, navigate_fn, filter_fn, rank_fn,
                      query, max_price):
        chain = cls()
        chain.add(ToolStep("search", lambda _p: search_fn(query)))
        chain.add(ToolStep("navigate", lambda p: navigate_fn(p)))
        chain.add(ToolStep("filter", lambda p: filter_fn(p, max_price)))
        chain.add(ToolStep("rank", lambda p: rank_fn(p)))
        return chain
