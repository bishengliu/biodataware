from django.db import models


# roles for access the database
class Role(models.Model):
    role = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.role
