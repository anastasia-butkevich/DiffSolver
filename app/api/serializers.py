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

    def get_x1_res(self, obj):
        """
        Calculate and return x values for Euler method.
        """
        func = obj.func
        x0, y0, h, b = obj.x0, obj.y0, obj.h, obj.b

        return self.euler_method(func, x0, y0, h, b)[0].tolist()

    def get_y1_res(self, obj):
        """
        Calculate and return y values for numerical methods.
        """
        func = obj.func
        x0, y0, h, b = obj.x0, obj.y0, obj.h, obj.b

        return self.euler_method(func, x0, y0, h, b)[1].tolist()
    
    def get_x2_res(self, obj):
        """
        Calculate and return x values for Euler-Cauchy method.
        """
        func = obj.func
        x0, y0, h, b = obj.x0, obj.y0, obj.h, obj.b

        return self.euler_cauchy_method(func, x0, y0, h, b)[0].tolist()

    def get_y2_res(self, obj):
        """
        Calculate and return y values for for Euler-Cauchy method.
        """
        func = obj.func
        x0, y0, h, b = obj.x0, obj.y0, obj.h, obj.b

        return self.euler_cauchy_method(func, x0, y0, h, b)[1].tolist()

    def euler_method(self, func: str, x0: float, y0: float, h: float, b: float) -> iter:
        """
        Euler Method implementation.
        """
        function = sp.sympify(func)
        x_range = np.arange(x0, b + h, h)

        n = len(x_range)

        y_vals = np.zeros(n)
        y_vals[0] = y0

        for i in range(1, n):
            y_vals[i] = y_vals[i - 1] + h * (function.subs({x: x_range[i - 1], y: y_vals[i - 1]}))

        return (x_range, y_vals)     

    def euler_cauchy_method(self, func: str, x0: float, y0: float, h: float, b: float) -> iter:
        """
        Euler-Cauchy Method implementation.
        """
        function = sp.sympify(func)
        x_range = np.arange(x0, b + h, h)

        n = len(x_range)

        y_vals = np.zeros(n)
        y_vals[0] = y0

        for i in range(1, n):
            f1 = function.subs({x: x_range[i - 1], y: y_vals[i - 1]})
            f2 = function.subs({x: x_range[i], y: (y_vals[i - 1] + h * f1)})

            y_vals[i] = y_vals[i - 1] + (h / 2) * (f1 + f2)

            
        return (x_range, y_vals)  
