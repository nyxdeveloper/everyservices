# django
from django.db import models

# импорты проекта
from everyservices.settings import AUTH_USER_MODEL


class HelpdeskMessage(models.Model):
    text = models.TextField()
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default=None,
                             related_name="sent_helpdesk_messages")
    to = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default=None,
                           related_name="received_helpdesk_messages", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения техподдержки"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.text}\n({self.created})"
