from django.db import models

# Create your models here.


class Temporary(models.Model):
    name = models.CharField(max_length=500)
    audio = models.FileField(upload_to='audio')
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
