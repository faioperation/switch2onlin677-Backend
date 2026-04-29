from django.db import models


class LeadPlatform(models.TextChoices):
    INSTAGRAM = "Instagram", "Instagram"
    FACEBOOK = "Facebook", "Facebook"
    WHATSAPP = "WhatsApp", "WhatsApp"
    OTHER = "Other", "Other"


class Lead(models.Model):
    user_id = models.CharField(
        max_length=255, blank=True, null=True
    )  # Meta/WhatsApp ID
    name = models.CharField(max_length=255)
    interested_product = models.CharField(max_length=255)
    platform = models.CharField(
        max_length=20, choices=LeadPlatform.choices, default=LeadPlatform.OTHER
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.name} - {self.interested_product} ({self.platform})"
