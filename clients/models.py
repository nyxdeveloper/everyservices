# django
from django.db import models
from django.utils import timezone

# импорты проекта
from everyservices.settings import AUTH_USER_MODEL
from everyservices.services import clean_phone


class Client(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clients")
    name = models.CharField(max_length=300)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, default="")
    blacklist = models.BooleanField(default=False)
    comment = models.TextField(default="", blank=True)
    blacklist_comment = models.TextField(default="", blank=True)
    created = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-created"]
        unique_together = ["user", "phone"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.blacklist:
            self.blacklist_comment = ""
        self.phone = clean_phone(self.phone)
        return super(Client, self).save()
