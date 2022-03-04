# django
from django.db import models

# импорты проекта
from everyservices.settings import AUTH_USER_MODEL


def services_img_path(instance, filename):
    return f"services/{instance.user.pk}/{instance.name}/{filename}"


class Service(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=250)
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    duration = models.TimeField()
    img = models.ImageField(upload_to=services_img_path, blank=True, null=True, default=None)
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["-cost"]
        unique_together = [["user", "name"]]

    def __str__(self):
        return self.name
