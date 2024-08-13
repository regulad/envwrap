"""envwrap - 🚀 Override function defaults with environment variables.

MIT License

Copyright © 2024 Parker Wahle

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""  # noqa: E501, B950

from __future__ import annotations

import inspect
import os
from functools import wraps
from inspect import signature
from typing import Optional, Dict, Callable

from typing_extensions import ParamSpec, TypeVar, Any, cast

F = TypeVar("F", bound=Callable[..., Any])


def get_root_function(func: F) -> F:
    """
    Get the root method of a method or function, unwrapping any decorators.

    Parameters
    ----------
    func : callable
        The method or function to get the root method of.

    Returns
    -------
    callable
        The root method of the given method or function.
    """
    while hasattr(func, "__func__"):
        func = func.__func__
    return func


def is_likely_method(func: Callable[..., Any]) -> bool:
    # Check if the first parameter is named 'self' or 'cls'
    params = inspect.signature(func).parameters
    if not params:
        return False
    first_param = next(iter(params.values()))
    return first_param.name in ("self", "cls")


P = ParamSpec("P")
R = TypeVar("R")


def envwrap(
    prefix: str,
    types: Optional[Dict[str, type]] = None,
    is_method: Optional[bool] = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Override parameter defaults via `os.environ[prefix + param_name]`.
    Maps UPPER_CASE env vars map to lower_case param names.
    camelCase isn't supported (because Windows ignores case).

    Precedence (highest first):

    - call (`foo(a=3)`)
    - environ (`FOO_A=2`)
    - signature (`def foo(a=1)`)

    Types are handled by typehints and are automatically determined, if possible.
    The types argument can be used to override the typehint inference.
    Envwrap will fallback to str if no typehint, override, or default value is found.

    `from __future__ import annotations` annotations are not supported.

    Parameters
    ----------
    prefix  : str
        Env var prefix, e.g. "FOO_"
    types  : dict, optional
        Fallback mappings `{'param_name': type, ...}` if types cannot be
        inferred from function signature.
        Consider using `types=collections.defaultdict(lambda: ast.literal_eval)`.
    is_method  : bool, optional
        Whether the function is a method. This will be detected automatically

    Examples
    --------
    ```
    $ cat foo.py
    from envwrap import envwrap
    @envwrap("FOO_")
    def test(a=1, b=2, c=3):
        print(f"received: a={a}, b={b}, c={c}")

    $ FOO_A=42 FOO_C=1337 python -c 'import foo; foo.test(c=99)'
    received: a=42, b=2, c=99
    ```
    """

    if types is None:
        types = {}

    def wrapper(func: Callable[P, R]) -> Callable[P, R]:
        params = signature(func).parameters
        root_function = get_root_function(func)

        is_method_explicit = is_method or is_likely_method(root_function)

        # if we are wrapping a method, we need to skip the first parameter
        params_method_safe = list(params.keys())[1:] if is_method_explicit else list(params.keys())

        if not callable(func):
            raise TypeError(f"{func} is not callable")

        @wraps(func)
        def final_callable(*args: P.args, **kwargs: P.kwargs) -> R:
            env_overrides = {
                k[len(prefix) :].lower(): v for k, v in os.environ.items() if k.startswith(prefix)
            }
            overrides = {k: v for k, v in env_overrides.items() if k in params_method_safe}

            for k in overrides:
                param = params[k]
                if param.annotation is not param.empty:  # typehints
                    for typ in getattr(param.annotation, "__args__", (param.annotation,)):
                        try:
                            overrides[k] = typ(overrides[k])
                        except Exception:
                            pass
                        else:
                            break
                elif param.default is not None:  # type of default value
                    overrides[k] = type(param.default)(overrides[k])
                else:
                    try:  # `types` fallback
                        overrides[k] = types[k](overrides[k])
                    except KeyError:  # keep unconverted (`str`)
                        pass

            default_kwargs = {k: v.default for k, v in params.items() if v.default is not v.empty}

            final_kwargs = cast(P.kwargs, {**default_kwargs, **overrides, **kwargs})

            return func(*args, **final_kwargs)

        return final_callable

    return wrapper


__all__ = ("envwrap",)
