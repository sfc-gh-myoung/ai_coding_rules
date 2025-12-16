# Python Classes: Design and Usage Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Python classes, OOP, inheritance, dataclasses, @property, class design, encapsulation, composition, Protocol, ABC, type hints
**TokenBudget:** ~2050
**ContextTier:** Medium
**Depends:** rules/200-python-core.md, rules/201-python-lint-format.md, rules/204-python-docs-comments.md

## Purpose
Provide practical, modern guidelines for when and how to use classes in Python, emphasizing composition over inheritance, type safety, encapsulation, and pythonic idioms that produce readable, maintainable, and testable code.

## Rule Scope

Class design patterns and usage in Python 3.11+ (data models, behavior, encapsulation, inheritance, protocols, ABCs)

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use @dataclass for data containers** - Prefer dataclass over manual __init__
- **Composition over inheritance** - Favor has-a over is-a relationships
- **Use @property for computed attributes** - Not Java-style getters/setters
- **Add type hints to all class methods** - Including __init__, properties, methods
- **frozen=True for immutable data** - Use @dataclass(frozen=True) when appropriate
- **Never create classes for single functions** - Use plain functions instead

**Quick Checklist:**
- [ ] Class justified (not just a function holder)
- [ ] @dataclass used for data containers
- [ ] Type hints on all methods
- [ ] Docstrings on class and public methods
- [ ] Properties used for computed attributes
- [ ] __repr__ provided (auto via dataclass)
- [ ] Composition preferred over inheritance

## Contract

<contract>
<inputs_prereqs>
Python 3.11+; project uses `uv` and Ruff (see `200-python-core.md`, `201-python-lint-format.md`)
</inputs_prereqs>

<mandatory>
`uv run` for execution; `uvx ruff` for lint/format; `pytest` via `uv run` for tests
</mandatory>

<forbidden>
Bare `python`, `pytest`, `ruff` (must use `uv run`/`uvx` per core rules)
</forbidden>

<steps>
1. Determine if a class is warranted vs function/module or `NamedTuple`/`dataclass`.
2. Choose composition over inheritance; select ABC/Protocol only when a stable interface is needed.
3. Add type hints to all public APIs; document with clear docstrings (`204-python-docs-comments.md`).
4. Apply encapsulation with properties; avoid Java-style getters/setters.
5. Use `@dataclass` (frozen if appropriate) for data containers; define equality/ordering deliberately.
6. Provide helpful `__repr__` for debugging; avoid logic in `__repr__`/`__str__` beyond formatting.
7. Manage resources via context managers or `contextlib` utilities when needed.
8. Validate design via lints, tests, and runtime checks where necessary.
</steps>

<output_format>
Focused diffs of class implementations and interfaces; runnable examples where applicable.
</output_format>

<validation>
`uvx ruff check .` and `uvx ruff format --check .` pass; `uv run pytest` passes; type-checkers (optional) report no issues for public APIs.
</validation>

<design_principles>
- **Prefer composition over inheritance:** Keep inheritance shallow. Use ABCs or Protocols to define capabilities.
- **Use dataclasses for data containers:** Prefer `@dataclass(slots=True, kw_only=True)` for clarity; consider `frozen=True` for immutability.
- **Encapsulation via properties:** Expose attributes with properties when invariants or validation are required; otherwise allow direct access.
- **Explicit public API:** Make intent clear with method and attribute names; prefix non-public helpers with a single underscore.
- **Type hints everywhere:** Public methods and constructors must have complete annotations; prefer standard collections types.
- **Small, cohesive classes:** Each class should have a single responsibility; avoid god objects.
- **Avoid side effects in `__init__`:** Only assign fields and do lightweight validation; perform I/O or heavy work in explicit methods.
- **Equality and ordering:** Implement value semantics deliberately using dataclass options or explicit dunder methods when domain requires it.
- **Good `__repr__`:** Make instances easy to debug; represent key fields, avoid leaking secrets.
- **Resource safety:** Use context managers (`__enter__`/`__exit__` or `contextlib.contextmanager`) for external resources.
- **Interfaces over concrete types:** Use `abc.ABC` + `@abstractmethod` for classic inheritance or `typing.Protocol` for structural typing.
- **Performance awareness:** Consider `slots=True` for many-instance classes to reduce memory; measure before optimizing.
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Mutable Default Arguments in Methods

**Problem:** Using mutable objects (lists, dicts, sets) as default argument values in function or method definitions.

**Why It Fails:** Default arguments are evaluated once at function definition, not at each call. The same mutable object is shared across all calls, causing mysterious bugs where data "leaks" between invocations.

**Correct Pattern:**
```python
# BAD: Mutable default argument
class DataCollector:
    def __init__(self, items=[]):  # Same list shared across all instances!
        self.items = items

# collector1.items.append("a") affects collector2.items

# GOOD: Use None and create new object in body
class DataCollector:
    def __init__(self, items: list | None = None):
        self.items = items if items is not None else []

# Each instance gets its own list
```

### Anti-Pattern 2: God Classes With Too Many Responsibilities

**Problem:** Creating classes that handle multiple unrelated concerns—data access, business logic, formatting, validation—all in one place.

**Why It Fails:** Violates Single Responsibility Principle. Changes to one feature risk breaking others. Testing requires mocking everything. Code reuse becomes impossible. Class grows indefinitely.

**Correct Pattern:**
```python
# BAD: God class doing everything
class UserManager:
    def create_user(self, data): ...
    def validate_email(self, email): ...
    def hash_password(self, password): ...
    def send_welcome_email(self, user): ...
    def generate_report(self, users): ...
    def export_to_csv(self, users): ...

# GOOD: Separate concerns into focused classes
class UserRepository:
    def create(self, user: User) -> User: ...

class UserValidator:
    def validate(self, data: dict) -> ValidationResult: ...

class EmailService:
    def send_welcome(self, user: User) -> None: ...
```

## Post-Execution Checklist
- [ ] Chosen class over functions for justified state + behavior needs
- [ ] Composition preferred; shallow or no inheritance
- [ ] `@dataclass` used for data carriers; `kw_only=True`; `slots=True` considered
- [ ] Public API fully type-annotated and documented with clear docstrings
- [ ] Encapsulation via properties where invariants/validation exist
- [ ] Helpful `__repr__` without secrets; equality semantics deliberate
- [ ] Resource management via context managers where applicable
- [ ] No heavy side effects in `__init__`; dependencies injected explicitly
- [ ] Lints and tests pass (`uvx ruff`, `uv run pytest`)

## Validation
- **Success Checks:** Ruff lint/format pass; tests cover main behaviors; class design adheres to principles; public API is stable and annotated.
- **Negative Tests:** Deep inheritance; mutable global state; side effects in constructors; missing type hints; leaking secrets in `__repr__`.

> **Investigation Required**
> When applying this rule:
> 1. **Read existing class definitions BEFORE suggesting changes** - Check current class structure, inheritance patterns
> 2. **Verify if dataclasses are used** - Check imports, existing patterns
> 3. **Never assume class design philosophy** - Check if project uses inheritance vs composition
> 4. **Check existing type hints** - Match project's type annotation style
> 5. **Read tests** - Understand how classes are tested and used
>
> **Anti-Pattern:**
> "Creating a dataclass... (without checking if project uses them)"
> "Adding inheritance... (without understanding existing patterns)"
>
> **Correct Pattern:**
> "Let me check your existing class designs first."
> [reads files, checks for dataclass usage, reviews inheritance patterns]
> "I see you use dataclasses for models and composition for services. Following this pattern..."

## Output Format Examples
```python
# Example skeleton applying class best practices
from dataclasses import dataclass
from typing import Protocol

class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

@dataclass(slots=True, kw_only=True, frozen=True)
class User:
    id: str
    name: str
    email: str

class Notifier:
    def __init__(self, sender: EmailSender) -> None:
        self._sender = sender

    def welcome(self, user: User) -> None:
        subject = f"Welcome, {user.name}!"
        self._sender.send(user.email, subject, "Thanks for joining.")
```

## References

### External Documentation
- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Dataclasses — Python docs](https://docs.python.org/3/library/dataclasses.html)
- [typing — Type Hints](https://docs.python.org/3/library/typing.html)
- [abc — Abstract Base Classes](https://docs.python.org/3/library/abc.html)
- [contextlib — Utilities for with-statement contexts](https://docs.python.org/3/library/contextlib.html)
- [Descriptors and properties](https://docs.python.org/3/howto/descriptor.html)

### Related Rules
- **Python Core**: `rules/200-python-core.md`
- **Python Lint/Format**: `rules/201-python-lint-format.md`
- **Python Project Setup**: `rules/203-python-project-setup.md`
- **Python Docs & Comments**: `rules/204-python-docs-comments.md`

## 1. Class Design Guidelines

### 1.1 When to use a class
- Rule: Use a class when modeling state + behavior that naturally belong together or when you need polymorphism via interfaces.
- Consider: Prefer pure functions and modules for stateless utilities.
- Consider: Use `@dataclass` for simple data carriers; elevate to rich domain objects only when behavior is justified.

### 1.2 Data classes
```python
from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True, kw_only=True, frozen=False)
class Customer:
    id: str
    name: str
    email: Optional[str] = None

    def update_email(self, new_email: str) -> None:
        self.email = new_email
```

- Requirement: Use `kw_only=True` for readability and future-proofing.
- Rule: Use `frozen=True` for value objects that should be immutable; implement methods that return new instances instead of mutating.
- Consider: `slots=True` to reduce memory footprint; avoid if you rely on dynamic attributes or pickling patterns.

### 1.3 Encapsulation and properties
```python
from dataclasses import dataclass

@dataclass(slots=True)
class Temperature:
    _celsius: float

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32
```

- Rule: Prefer properties over explicit `get_*`/`set_*` methods.
- Avoid: Hidden side effects in getters/setters; keep them lightweight.

### 1.4 Interfaces with ABCs and Protocols
```python
from abc import ABC, abstractmethod
from typing import Protocol

class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None: ...

    @abstractmethod
    def set(self, key: str, value: str) -> None: ...

class KeyValueStore(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...
```

- Requirement: Use `Protocol` for duck-typed interfaces; use ABCs when you need shared base logic or registration.
- Avoid: Deep inheritance hierarchies (>2 levels). Prefer composing smaller objects.

### 1.5 Resource management
```python
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def opened(path: str) -> Iterator[object]:
    f = open(path, "rb")
    try:
        yield f
    finally:
        f.close()
```

- Rule: Use context managers for files, sockets, locks, transactions.
- Consider: Implement `__enter__`/`__exit__` on classes that own the resource lifecycle.

### 1.6 Special methods and representation
```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: float
    y: float

    def __repr__(self) -> str:  # helpful for debugging/logging
        return f"Point(x={self.x!r}, y={self.y!r})"

    def __str__(self) -> str:  # user-friendly
        return f"({self.x}, {this.y})"
```

- Requirement: Provide `__repr__` suitable for developers; avoid including secrets.
- Consider: Implement `__eq__`/`__hash__` for value semantics; dataclasses can generate these.

### 1.7 Initialization and dependency injection
```python
class Service:
    def __init__(self, repository: "Repository") -> None:
        self._repo = repository

    def process(self, item_id: str) -> None:
        entity = self._repo.load(item_id)
        # ... do work ...
```

- Rule: Inject dependencies via `__init__`; avoid reaching for globals/singletons.
- Avoid: Performing I/O or long-running work in `__init__`.

### 1.8 Testing and seams
- Requirement: Design for testability by accepting interfaces (Protocols/ABCs) that can be faked/mocked.
- Rule: Keep classes small to simplify unit tests; separate pure logic from I/O.

### 1.9 Performance considerations
- Consider: `slots=True` for high-volume instances.
- Consider: Avoid per-instance `__dict__` unless needed.
- Consider: Use `functools.cached_property` for expensive derived values.
