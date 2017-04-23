"""This module contains the TimeFunction"""

import pandas as pd
from ..functions.wrapper import BaseWrapper


class TimeFunction:
    """Convert time series index into time series values while applying given
    functions.
    
    The `condition` defines the valid range of values. Any values which do not
    satisfy the condition are discarded.
    
    In addition, a TimeFunction may have `vectorized` and `iterated` implemen-
    tations. The iterated function is particularly interesting when a 
    condition is given. As soon as the condition evaluates to False, the
    function will end to compute further values. This has performance benefits
    on large time series.
    
    """

    def __init__(self, vectorized=None, iterated=None, condition=None):
        """Initializes TimeFunction instance.
        
        """

        if not (vectorized or iterated):
            raise ValueError("At least one function / function generator needs"
                             "to be provided for 'vectorized' or 'iterated'")

        self.vectorized = vectorized
        self.iterated = iterated
        self.condition = condition

    def generate(self, time_units):
        """Apply a time function to given `time_units`. 
        
        If condition is set, it will try to use the iterating approach.
        Otherwise prefers the vectorized approach.

        """

        if self.condition:
            if self.iterated:
                return self._generate_iterated(time_units)

        if self.vectorized:
            return self._generate_vectorized(time_units)

        return self._generate_iterated(time_units)

    def _evaluate_function(self, function):
        """Check type of function. If function takes no arguments it is 
        expected to be a function generator. If it takes exactly one argument,
        it is expected to be a constant function.
        
        """

        if issubclass(function.__class__, BaseWrapper):
            return function()

        try:
            # get number of optional keyword arguments
            try:
                kwargs_count = len(function.__defaults__)
            except TypeError:
                kwargs_count = 0

            arg_names = function.__code__.co_varnames
            karg_count = len(arg_names) - kwargs_count

        except AttributeError:
            return function

        # not more than one karg allowed
        if karg_count > 1:
            raise ValueError("Function passed to TimeFunction needs to have 0 "
                             "arguments for a function generator or 1 arugment"
                             " for a constant function. Passed function has {}"
                             " arguments.".format(karg_count))

        # check for functions with no kargs and a size kwarg
        elif karg_count == 0 and "size" in arg_names:
            return lambda x: function(size=x.shape[0])

        # finalized function
        elif karg_count == 1:
            return function

        else:
            return self._evaluate_function(function())

    def _generate_vectorized(self, time_units):
        """Generate values in a vectorized fashion.
        
        """

        time_func = self._evaluate_function(self.vectorized)
        time_values = time_func(time_units)

        if not issubclass(time_values.__class__, pd.Series):
            time_values = pd.Series(time_values, index=time_units.index)

        if self.condition:
            mask = self.condition(time_values)
            time_values = time_values[mask]

        return time_values

    def _generate_iterated(self, time_units):
        """Generate values in an iterated fashion. 
        
        Uses generator to return values one after another as long as condition
        holds.
        
        """

        time_func = self._evaluate_function(self.iterated)

        if self.condition:
            def yield_values():
                iterator = iter(time_units)
                current_val = time_func(next(iterator))
                while self.condition(current_val):
                    yield current_val
                    current_val = time_func(next(iterator))

            values = list(yield_values())
            index = time_units[:len(values)].index
            time_values = pd.Series(values, index)

        else:
            time_values = time_units.apply(time_func)

        return time_values
