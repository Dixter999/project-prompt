"""
Calculator module for basic arithmetic operations.

This module provides a Calculator class with methods for addition, 
subtraction, multiplication, and division operations.
"""

from typing import Union, List, Dict, Any, Optional, Tuple
import math

Number = Union[int, float]


class CalculationError(Exception):
    """Exception raised for errors in the calculator operations."""
    pass


class Calculator:
    """
    A calculator class that provides basic arithmetic operations.
    
    Attributes:
        precision (int): Number of decimal places for rounding results
        history (List[Dict[str, Any]]): History of operations performed
    """
    
    def __init__(self, precision: int = 2):
        """
        Initialize a Calculator instance.
        
        Args:
            precision: Number of decimal places for rounding results (default: 2)
        """
        self.precision: int = precision
        self.history: List[Dict[str, Any]] = []
        
    def add(self, a: Number, b: Number) -> Number:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The sum of a and b
        """
        result = a + b
        self._log_operation("add", [a, b], result)
        return self._round(result)
    
    def subtract(self, a: Number, b: Number) -> Number:
        """
        Subtract b from a.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The result of a - b
        """
        result = a - b
        self._log_operation("subtract", [a, b], result)
        return self._round(result)
    
    def multiply(self, a: Number, b: Number) -> Number:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The product of a and b
        """
        result = a * b
        self._log_operation("multiply", [a, b], result)
        return self._round(result)
    
    def divide(self, a: Number, b: Number) -> Number:
        """
        Divide a by b.
        
        Args:
            a: First number (numerator)
            b: Second number (denominator)
            
        Returns:
            The result of a / b
            
        Raises:
            CalculationError: If b is zero
        """
        if b == 0:
            self._log_operation("divide", [a, b], None, error="Division by zero")
            raise CalculationError("Cannot divide by zero")
            
        result = a / b
        self._log_operation("divide", [a, b], result)
        return self._round(result)
    
    def power(self, base: Number, exponent: Number) -> Number:
        """
        Raise base to the power of exponent.
        
        Args:
            base: The base value
            exponent: The exponent value
            
        Returns:
            base raised to the power of exponent
        """
        result = math.pow(base, exponent)
        self._log_operation("power", [base, exponent], result)
        return self._round(result)
    
    def square_root(self, value: Number) -> Number:
        """
        Calculate the square root of a value.
        
        Args:
            value: The value to calculate the square root of
            
        Returns:
            The square root of the value
            
        Raises:
            CalculationError: If value is negative
        """
        if value < 0:
            self._log_operation("square_root", [value], None, error="Cannot calculate square root of negative number")
            raise CalculationError("Cannot calculate square root of negative number")
            
        result = math.sqrt(value)
        self._log_operation("square_root", [value], result)
        return self._round(result)
    
    def clear_history(self) -> None:
        """Clear the operation history."""
        self.history = []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the operation history.
        
        Returns:
            A list of operation records
        """
        return self.history.copy()
    
    def _round(self, value: Number) -> Number:
        """
        Round a value to the specified precision.
        
        Args:
            value: Value to round
            
        Returns:
            Rounded value
        """
        return round(value, self.precision)
    
    def _log_operation(self, 
                      operation: str, 
                      operands: List[Number], 
                      result: Optional[Number], 
                      error: Optional[str] = None) -> None:
        """
        Log an operation to the history.
        
        Args:
            operation: Name of the operation
            operands: List of operands
            result: Result of the operation
            error: Error message if the operation failed
        """
        self.history.append({
            "operation": operation,
            "operands": operands,
            "result": result,
            "error": error
        })
