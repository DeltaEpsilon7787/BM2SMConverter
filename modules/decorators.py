def transform_args(*arg_lambdas, **kwarg_lambdas):
    """Construct a decorator that attempts to transform arguments before calling the function.

    Arguments:
        *arg_lambdas (Union[Ellipsis, Callable, List[Callable]]):
            Transformers for positional arguments.

            type: Ellipsis:
                Value remains unchanged (identity function).

            type: Callable -> List[Callable]

            type: List[Callable]
                Reduce is used on the chain with this value being initial.

        **kwarg_lambdas (Union[Ellipsis, Callable, List[Callable]]):
            For keyword arguments.

            Same rules apply as for arg_lambdas.

            If key is str like @1, @2, @kwarg etc. and value is str, then if ValueError is raised by function,
            it will be reraised with this message.

    Notes:
        kwarg lambda is only applied when the function is explicitly called with this keyword argument
        Initial kwarg values are NOT transformed.

    Raises:
        ValueError:
            If ValueError is raised during transform by one of the functions.
    """
    positional_transform_error_message = """Positional transform failed
    Func: {func}
    Arg#: {arg_pos}
    Value: {arg_value}
    Value type: {value_type}
    Chain#: {chain_pos}
    Message: {message}"""
    keyword_transform_error_message = """Keyword transform failed
    Func: {func}
    Kwarg: {kwarg}
    Value: {kwarg_value}
    Value type: {value_type}
    Chain#: {chain_pos}
    Message: {message}"""

    def decorator(func):
        from functools import wraps
        from itertools import count

        @wraps(func)
        def transformer(*args, **kwargs):
            nonlocal arg_lambdas

            modified_args = []
            modified_kwargs = {}

            if len(args) > len(arg_lambdas):
                arg_lambdas = arg_lambdas.copy()
                arg_lambdas += [Ellipsis] * (len(args) - len(arg_lambdas))

            for arg_pos, arg_value, transform_source in zip(count(), args, arg_lambdas):
                if transform_source is Ellipsis:
                    modified_args.append(arg_value)
                    continue
                elif callable(transform_source):
                    transform_source = (transform_source,)
                for chain_pos, transform_func in enumerate(transform_source):
                    try:
                        arg_value = transform_func(arg_value)
                    except ValueError as E:
                        possible_name = '@' + str(arg_pos)
                        message = kwarg_lambdas.get(possible_name, E.args[0] if len(E.args) else "")
                        message = positional_transform_error_message.format(func=func.__name__,
                                                                            arg_pos=arg_pos,
                                                                            arg_value=arg_value,
                                                                            value_type=type(arg_value),
                                                                            chain_pos=chain_pos,
                                                                            message=message)
                        raise ValueError(message)
                modified_args.append(arg_value)

            for kwarg_name, kwarg_value in kwargs.items():
                transform_source = kwarg_lambdas.get(kwarg_name, Ellipsis)
                if transform_source is Ellipsis:
                    modified_kwargs[kwarg_name] = kwarg_value
                    continue
                elif callable(transform_source):
                    transform_source = (transform_source,)
                for chain_pos, transform_func in zip(count(0), transform_source):
                    try:
                        kwarg_value = transform_func(kwarg_value)
                    except ValueError as E:
                        possible_name = '@' + kwarg_name
                        message = E.args[0] if len(E.args) else ""
                        if possible_name in kwarg_lambdas:
                            message = kwarg_lambdas.get(possible_name)
                        message = keyword_transform_error_message.format(func=func.__name__,
                                                                         kwarg=kwarg_name,
                                                                         kwarg_value=kwarg_value,
                                                                         value_type=type(kwarg_value),
                                                                         chain_pos=chain_pos,
                                                                         message=message)
                        raise ValueError(message)
                modified_kwargs[kwarg_name] = kwarg_value
            return func(*modified_args, **modified_kwargs)

        return transformer

    return decorator


def transform_return(return_transform, return_message=Ellipsis):
    """A limited version of transform_args that only accepts one transform func and applies it
    to return value of the function

    Arguments:
        return_transform (Union[Callable, List[Callable]):
            type: Callable -> List[Callable]

            type: List[Callable]
                Reduce is used on the chain with return value being initial

        return_message (Ellipsis, str):
            If not Ellipsis, then if ValueError is raised by the function, it will be reraised with this message

    Raises:
        ValueError:
            If ValueError is raised during transform.
"""

    return_transform_error_message = """Return transform failed
    Func: {func}
    Value: {return_value}
    Message: {message}"""

    def decorator(func):
        from functools import wraps

        @wraps(func)
        def transformer(*args, **kwargs):
            value = func(*args, **kwargs)
            try:
                value = return_transform(value)
            except ValueError as E:
                message = E.args[0] if len(E.args) else ''
                if return_message is not Ellipsis:
                    message = return_message
                message = return_transform_error_message.format(func=func.__name__,
                                                                return_value=value,
                                                                message=message)
                raise ValueError(message)
            return value

        return transformer

    return decorator
