# Python Classes: Design and Usage Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** Python classes, OOP, inheritance, dataclasses, @property, class design, encapsulation, composition, Protocol, ABC, type hints
**TokenBudget:** ~4050
**ContextTier:** Medium
**Depends:** 200-python-core.md, 201-python-lint-format.md, 204-python-docs.md
**LoadTrigger:** kw:class, kw:oop, kw:dataclass

## Scope

**What This Rule Covers:**
Practical, modern guidelines for when and how to use classes in Python, emphasizing composition over inheritance, type safety, encapsulation, and pythonic idioms. Covers dataclasses, properties, protocols, ABCs, resource management, and class design patterns that produce readable, maintainable, and testable code.

**When to Load This Rule:**
- Designing new Python classes
- Refactoring procedural code to OOP
- Choosing between classes, functions, or dataclasses
- Implementing inheritance or composition patterns
- Using protocols or abstract base classes
- Troubleshooting class design issues
- Reviewing OOP code for best practices

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Python foundation patterns
- **201-python-lint-format.md** - Code quality and linting
- **204-python-docs.md** - Documentation standards

**Related:**
- **206-python-pytest.md** - Testing class-based code

### External Documentation

- [Python Data Classes](https://docs.python.org/3/library/dataclasses.html) - dataclass module
- [PEP 544](https://peps.python.org/pep-0544/) - Protocols (structural subtyping)
- [Python ABC Module](https://docs.python.org/3/library/abc.html) - Abstract base classes

## Contract

### Inputs and Prerequisites

- Python 3.11+ codebase
- Project uses uv and Ruff
- Understanding of OOP concepts
- Familiarity with type hints

### Mandatory

- **Use @dataclass for data containers** - Prefer dataclass over manual __init__
- **Composition over inheritance** - Favor has-a over is-a relationships
- **Use @property for computed attributes** - Not Java-style getters/setters
- **Add type hints to all class methods** - Including __init__, properties, methods
- **frozen=True for immutable data** - Use @dataclass(frozen=True) for value objects and read-only configuration
- **Never create classes for single functions** - Use plain functions instead

### Forbidden

- Classes that are just function holders
- Java-style getters/setters (use @property instead)
- Deep inheritance hierarchies (favor composition)
- Missing type hints on class methods
- Bare command execution (must use `uv run`/`uvx`)

### Execution Steps

1. Determine if a class is warranted vs function/module or dataclass
2. Choose composition over inheritance; use ABC/Protocol only for stable interfaces
3. Add type hints to all public APIs; document with clear docstrings
4. Apply encapsulation with properties; avoid Java-style getters/setters
5. Use @dataclass (frozen if appropriate) for data containers
6. Provide helpful __repr__ for debugging
7. Manage resources via context managers when needed
8. Validate design via lints, tests, and runtime checks

### Output Format

Class implementations produce:
- Type-hinted class definitions
- Dataclasses for data containers
- Properties for computed attributes
- Context managers for resource management
- Protocols or ABCs for stable interfaces

### Validation

**Pre-Task-Completion Checks:**
- [ ] Class justified (not just a function holder)
- [ ] @dataclass used for data containers
- [ ] Type hints on all methods
- [ ] Docstrings on class and public methods
- [ ] Properties used for computed attributes
- [ ] __repr__ provided (auto via dataclass)
- [ ] Composition preferred over inheritance

**Success Criteria:**
- `uvx ruff check .` passes
- `uvx ruff format --check .` passes
- `uv run pytest` passes
- Type-checkers (optional) report no issues for public APIs

**Negative Tests:**
- Classes without justification should be refactored to functions
- Missing type hints should trigger linting errors
- Improper inheritance should be flagged in reviews

### Design Principles

- **Simplicity:** Use classes only when justified; prefer functions and dataclasses
- **Composition:** Favor has-a over is-a relationships
- **Pythonic:** Use @property, not Java-style getters/setters
- **Type safety:** Add type hints to all class methods
- **Immutability:** Use frozen=True for immutable data

### Post-Execution Checklist

- [ ] Class justified (not just a function holder)
- [ ] @dataclass used for data containers
- [ ] Type hints on all methods and __init__
- [ ] Docstrings on class and public methods
- [ ] Properties used for computed attributes
- [ ] __repr__ provided (auto via dataclass or custom)
- [ ] Composition preferred over inheritance
- [ ] Resource management via context managers (if applicable)

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

## Implementation Details

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

## Class Design Guidelines

Directive levels: **Mandatory** = must always follow. **Rule** = strong default, override only with documented reason. **Avoid** = don't unless justified by specific constraint.

### 1.1 When to use a class
- Rule: Use a class when modeling state + behavior that naturally belong together or when you need polymorphism via interfaces.
- Rule: When module has no shared state, use functions instead of classes.
- Rule: Use `@dataclass` for simple data carriers; elevate to rich domain objects only when the class needs methods that mutate state, enforce invariants, or coordinate with external resources.

### 1.2 Data classes
```python
from dataclasses import dataclass

@dataclass(slots=True, kw_only=True, frozen=False)
class Customer:
    id: str
    name: str
    email: str | None = None

    def update_email(self, new_email: str) -> None:
        self.email = new_email
```

- Rule: Use `kw_only=True` for readability and future-proofing.
- Rule: Use `frozen=True` for value objects that should be immutable; implement methods that return new instances instead of mutating.

  ```python
  @dataclass(frozen=True)
  class Point:
      x: float
      y: float

  # Attempting mutation raises FrozenInstanceError:
  # point = Point(1.0, 2.0)
  # point.x = 3.0  # FrozenInstanceError

  # To "modify" frozen dataclasses, create a new instance:
  from dataclasses import replace

  point = Point(1.0, 2.0)
  moved = replace(point, x=3.0)  # New instance with x=3.0
  ```

  **When to use `frozen=True`:**
  - Value objects (coordinates, money, config)
  - Dictionary keys (frozen dataclasses are hashable)
  - Thread-shared data (immutable = thread-safe)

  **When NOT to use `frozen=True`:**
  - Objects that accumulate state over time (use regular dataclass)
  - Performance-critical code with many mutations (replace() creates copies)
- Rule: When creating >1000 instances, add `slots=True` to reduce memory footprint; avoid if: (1) code uses `__dict__` directly, (2) code uses `setattr()` with dynamic keys, or (3) code uses `pickle.dumps()`/`loads()` on instances.

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
- Avoid: Hidden side effects in getters/setters. Properties must execute in O(1) time with no I/O, no database calls, and no network requests.

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

- Rule: Use `Protocol` for duck-typed interfaces; use ABCs when you need shared base logic or registration.
- Inheritance is acceptable when ANY of these conditions is met:
  1. **Framework requirement:** The base class is from a framework (e.g., `BaseModel`, `TestCase`, `APIView`) and inheritance is the intended extension mechanism
  2. **IS-A relationship:** The subclass truly IS-A specialization (e.g., `HttpError` IS-A `AppError`), not just shares some methods
  3. **Abstract interface:** The base class defines an abstract interface with `ABC` and all methods are `@abstractmethod`
  4. **Mixin with single responsibility:** The mixin adds exactly one capability (e.g., `TimestampMixin` adds `created_at`/`updated_at`)

  Inheritance is **NOT justified** when:
  - You just want to reuse some methods: use composition instead
  - The "base class" has state that the child doesn't need: use composition instead
  - You have more than 2 levels of inheritance: flatten with composition instead
- Avoid: Deep inheritance hierarchies (>2 levels). Prefer composing smaller objects.

### Abstract Interfaces

When you need to define an interface that multiple classes must implement:

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    """Interface for data repositories."""

    @abstractmethod
    def get(self, id: str) -> Model:
        """Retrieve a model by ID."""
        ...

    @abstractmethod
    def save(self, model: Model) -> None:
        """Persist a model."""
        ...

class PostgresRepository(Repository):
    def get(self, id: str) -> Model:
        return self.db.query(Model).get(id)

    def save(self, model: Model) -> None:
        self.db.add(model)
        self.db.commit()
```

**Rules:**
- All methods in ABC should be `@abstractmethod` (no partial interfaces)
- Use `Protocol` (typing) for structural subtyping instead of ABC when duck typing is preferred
- Maximum 1 level of abstract class hierarchy

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
- Rule: When class owns resources (files, connections, locks), implement `__enter__`/`__exit__` for context manager support.

**Class-based context manager:**
```python
class DatabaseConnection:
    """Database connection with automatic cleanup."""

    def __init__(self, url: str) -> None:
        self.url = url
        self._conn: Connection | None = None

    def __enter__(self) -> Connection:
        self._conn = connect(self.url)
        return self._conn

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._conn is not None:
            if exc_type is not None:
                self._conn.rollback()
            self._conn.close()
            self._conn = None
```

**Decision:** Use class-based when the context manager has state or complex cleanup. Use `@contextmanager` for simple acquire/release patterns.

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
        return f"({self.x}, {self.y})"
```

- Rule: Provide `__repr__` suitable for developers; avoid including secrets.
- Rule: Implement `__eq__`/`__hash__` for value semantics; dataclasses can generate these.

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
- Rule: Design for testability by accepting interfaces (Protocols/ABCs) that can be faked/mocked.
- Rule: Keep classes small to simplify unit tests; separate pure logic from I/O.

### 1.9 Performance considerations
- Rule: When creating >1000 instances, use `slots=True` for memory efficiency.
- Rule: Avoid per-instance `__dict__` unless dynamic attributes are needed.
- Rule: Use `functools.cached_property` for computations taking >1ms or involving >1000 iterations (no I/O, no database calls, O(1) complexity for the cache lookup).

### Memory Optimization with __slots__

Use `__slots__` for classes with many instances (>1000):

```python
class Sensor:
    __slots__ = ("id", "value", "timestamp")

    def __init__(self, id: str, value: float, timestamp: datetime) -> None:
        self.id = id
        self.value = value
        self.timestamp = timestamp
```

**Benefits:** ~40% less memory per instance, slightly faster attribute access.
**Trade-off:** No `__dict__`, cannot add arbitrary attributes at runtime.
**Prefer dataclasses with `slots=True` (Python 3.10+):**
```python
@dataclass(slots=True)
class Sensor:
    id: str
    value: float
    timestamp: datetime
```
