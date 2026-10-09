---
schema_version: v4.0
rule_version: v5.0.0
description: "Practical, modern guidelines for when and how to use classes in Python, emphasizing composition over inheritance, type safety, encapsulation, and pythonic idioms. Covers dataclasses, properties,"
last_updated: 2026-10-06
keywords:
  - kw:dataclass decorator
  - kw:composition over inheritance
  - kw:@property decorator
  - kw:Protocol structural subtyping
  - kw:frozen immutable dataclass
  - kw:context manager resource
  - kw:pytest
token_budget: ~1100
context_tier: Medium
depends:
  required:
    - 200-python-core.md  # Python foundation patterns
  optional:
    - 206-python-pytest.md  # Testing class-based code
---
# Python Classes: Design and Usage

## Scope

**What This Rule Covers:**
Choosing functions/dataclasses/classes, composition/interfaces, invariants, value semantics, dependency injection and resource lifecycle.

**When to Load This Rule:**
When designing/reviewing Python classes, properties, dataclasses, Protocol/ABC boundaries or owned resources.

## Contract

### Inputs and Prerequisites

- Existing class/caller/test architecture, actual Python support and type/lint configuration.
- Required state/behavior/invariants, resource/concurrency requirements and measured performance concerns.

### Mandatory

- Use a class for meaningful state+behavior or polymorphism, not a one-function holder. Prefer modules/functions for stateless work and dataclasses for data carriers when compatible with existing design.
- Prefer composition for reuse; inheritance is appropriate for true specialization, framework contracts, focused mixins or stable abstract interfaces. Avoid depth/abstract hierarchies that obscure behavior, not an arbitrary universal two-level ban.
- Type public methods/initializers/properties and document lifecycle/effects. Inject dependencies rather than hidden globals/singletons; avoid unrequested I/O in constructors.
- Use default_factory or deliberate None defaults for per-instance mutable state; decide whether supplied containers are borrowed or copied and document mutation ownership.
- frozen dataclasses support reassignment prevention, not deep immutability or universal thread safety/hashability. Mutable fields still require care; test equality/hash behavior against real value semantics.
- Choose slots/keyword-only fields based on API/memory needs; verify dynamic attributes, inheritance, weak references, serialization and cached_property compatibility. Do not promise fixed memory savings or optimize at an invented instance-count threshold.
- Properties expose cheap predictable attributes; do not hide network/database I/O or expensive unpredictable work in getters. Cache only with explicit invalidation/lifetime/thread considerations and measured need.
- Validate invariants at construction and mutation boundaries; a validating setter does not protect a bypassing dataclass initializer.
- Protocol provides structural contracts; ABC can include shared logic as well as abstract operations. Do not force every ABC member abstract or treat runtime type checks as static protocol verification.
- Owned files/connections/locks use context managers/finally. Preserve exceptions and guarantee cleanup without silently swallowing failure; transaction handling reflects actual scope.
- repr/debug output informative but excludes secrets. Implement equality/hash/str only when their semantics matter; keep pure logic separable from I/O for tests.

### Execution Steps

1. Read existing class/callers/tests, identify required invariants and decide function/data/class abstraction.
2. Apply minimal composition/interface design and typed constructor/public methods.
3. Define ownership, mutable defaults, invariants, value semantics and resource cleanup explicitly.
4. Review property/caching/slots implications against actual use and supported Python, not generic thresholds.
5. Run lint/format/types and tests covering mutation isolation, invalid inputs, cleanup on exceptions and public compatibility.

### Validation

- Abstraction justified, responsibilities cohesive and dependency seams explicit.
- Mutable state not shared accidentally, frozen/hash/thread claims accurate and invariants cannot be bypassed through initialization.
- Property/cache/resource behavior predictable; exception cleanup and concurrency tested where relevant.
- Public methods typed/documented, repr safe, caller/equality/serialization compatibility maintained.
- Actual project lint/format/type/test gates pass; no optional type check claim contrary to Python core.

## References

- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [Python ABC](https://docs.python.org/3/library/abc.html)
- [Python contextlib](https://docs.python.org/3/library/contextlib.html)
- [Python cached_property](https://docs.python.org/3/library/functools.html#functools.cached_property)
