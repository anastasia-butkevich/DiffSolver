from django.db import models

# Create your models here.
class DifferentialEq(models.Model):
    # Record name
    name = models.CharField(max_length=100, unique=True)

    # Analitical expression of the function
    func = models.CharField(max_length=100)

    # Parameters
    x0 = models.FloatField()
    y0 = models.FloatField()
    b = models.FloatField()
    h = models.FloatField()

    def __str__(self) -> str:
        return (f"Name: {self.name}, function: {self.func},\n"
                f"condition: y({self.x0}) = {self.y0},\n"
                f"boundaries: [{self.x0}, {self.b}], step: {self.h}")
