import sympy as sp
import numpy as np

from rest_framework import serializers
from app.models import DifferentialEq


x, y = sp.symbols('x y')


class DifferentialEqSerializer(serializers.ModelSerializer):
    x1_res = serializers.SerializerMethodField()
    y1_res = serializers.SerializerMethodField()
    x2_res = serializers.SerializerMethodField()
    y2_res = serializers.SerializerMethodField()

    class Meta:
        model = DifferentialEq
        fields = '__all__'

    def validate_func(self, f):
        """
        Validates that the function is a valid mathematical expression.
        """
        if ',' in f:
            raise serializers.ValidationError("Function should use dots, not commas.")
        try:
            sp.sympify(f)
        except (sp.SympifyError, TypeError):
            raise serializers.ValidationError("Function is not a valid expression.")
        return f
    
    def validate(self, data):
        """
        Validates x0 (a), b and h.
        """
        if data['h'] <= 0:
            raise serializers.ValidationError("Step size 'h' must be non-zero positive value.")
        if data['b'] <= data['x0']:
            raise serializers.ValidationError("'b' must be greater than 'x0'.")
        return data
    
    def _get_euler_results(self, obj):
        if not hasattr(self, '_euler_cache'):
            self._euler_cache = {}

        key = (obj.func, obj.x0, obj.y0, obj.h, obj.b)
        if key not in self._euler_cache:
            self._euler_cache[key] = self.euler_method(obj.func, obj.x0, obj.y0, obj.h, obj.b)
        return self._euler_cache[key]

    def _get_euler_cauchy_results(self, obj):
        if not hasattr(self, '_euler_cauchy_cache'):
            self._euler_cauchy_cache = {}

        key = (obj.func, obj.x0, obj.y0, obj.h, obj.b)
        if key not in self._euler_cauchy_cache:
            self._euler_cauchy_cache[key] = self.euler_cauchy_method(obj.func, obj.x0, obj.y0, obj.h, obj.b)
        return self._euler_cauchy_cache[key]

    def get_x1_res(self, obj):
        """
        Calculate and return x values for Euler method.
        """
        x_vals, _ = self._get_euler_results(obj)
        return x_vals.tolist()

    def get_y1_res(self, obj):
        """
        Calculate and return y values for numerical methods.
        """
        _, y_vals = self._get_euler_results(obj)
        return y_vals.tolist()
    
    def get_x2_res(self, obj):
        """
        Calculate and return x values for Euler Method.
        """
        x_vals, _ = self._get_euler_cauchy_results(obj)
        return x_vals.tolist()

    def get_y2_res(self, obj):
        """
        Calculate and return y values for for Euler-Cauchy Method.
        """
        _, y_vals = self._get_euler_cauchy_results(obj)
        return y_vals.tolist()

    def euler_method(self, func: str, x0: float, y0: float, h: float, b: float) -> tuple[np.ndarray, np.ndarray]:
        """
        Euler Method implementation.
        """
        symbolic_expr = sp.sympify(func)
        f = sp.lambdify((x, y), symbolic_expr, "numpy")
        
        n_steps = int(np.ceil((b - x0) / h)) + 1
        x_range = np.linspace(x0, x0 + h * (n_steps - 1), n_steps)
        
        y_vals = np.zeros(n_steps)
        y_vals[0] = y0

        for i in range(1, n_steps):
            y_vals[i] = y_vals[i - 1] + h * f(x_range[i - 1], y_vals[i - 1])
        return (x_range, y_vals)

    def euler_cauchy_method(self, func: str, x0: float, y0: float, h: float, b: float) -> tuple[np.ndarray, np.ndarray]:
        """
        Euler-Cauchy Method implementation.
        """
        symbolic_expr = sp.sympify(func)
        f = sp.lambdify((x, y), symbolic_expr, "numpy")
        
        n_steps = int(np.ceil((b - x0) / h)) + 1
        x_range = np.linspace(x0, x0 + h * (n_steps - 1), n_steps)
        
        y_vals = np.zeros(n_steps)
        y_vals[0] = y0

        for i in range(1, n_steps):
            f1 = f(x_range[i - 1], y_vals[i - 1])
            f2 = f(x_range[i], y_vals[i - 1] + h * f1)
            y_vals[i] = y_vals[i - 1] + (h / 2) * (f1 + f2)
        return (x_range, y_vals)
