import os
import uuid

from django.contrib.auth.models import User
from django.core.files.storage import default_storage as storage
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from PIL import Image


class DirectiveDiagnosis(models.Model):
    name = models.CharField(
        max_length=250, verbose_name="Applicable diagnosis for directive")

    def __str__(self):
        return self.name


class DirectivePopulation(models.Model):
    name = models.CharField(
        max_length=250, verbose_name="Applicable population for directive")

    def __str__(self):
        return self.name


class DirectivePage(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name="Random string for url",)
    title = models.CharField(
        max_length=75,
        verbose_name="Directive Title")
    population = models.ManyToManyField(
        DirectivePopulation, related_name='educationposts',
        verbose_name="Target Population", help_text="*Use ctrl+click on windows, or cmd+click on a Mac to select more than one.")
    diagnosis = models.ManyToManyField(
        DirectiveDiagnosis, related_name='educationposts',
        verbose_name="Target Diagnosis", help_text="*Use ctrl+click on windows, or cmd+click on a Mac to select more than one.")
    intro = models.TextField(max_length=300, blank=False, null=True,
                             verbose_name="Directive Introduction")
    discussion = models.TextField(
        max_length=1000, blank=False, null=True, verbose_name="Directive Dissucssion")
    created = models.DateTimeField(null=True, editable=False)
    updated = models.DateTimeField(null=True)
    posted_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super(DirectivePage, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail_directive_post', args=[self.uuid])

    def __str__(self):
        return self.title


class DirectiveObjective(models.Model):
    objective = models.TextField(
        max_length=250, verbose_name="Directive Objectives", null=False, blank=False)
    directive = models.ForeignKey(
        DirectivePage, on_delete=models.CASCADE, related_name='objectives', null=False, blank=False)

    def __str__(self):
        return self.objective


class DirectiveMaterial(models.Model):
    material = models.TextField(
        max_length=250, verbose_name="Directive Materials", null=False, blank=False)
    directive = models.ForeignKey(
        DirectivePage, on_delete=models.CASCADE, related_name='materials', null=False, blank=False)

    def __str__(self):
        return self.material


class DirectiveInstruction(models.Model):
    instruction = models.TextField(
        max_length=250, verbose_name="Directive Instruction", null=False, blank=False)
    directive = models.ForeignKey(
        DirectivePage, on_delete=models.CASCADE, related_name='instructions', null=False, blank=False)

    def __str__(self):
        return self.instruction


class DirectiveImage(models.Model):
    image = models.ImageField(upload_to='directives')
    directive = models.ForeignKey(
        DirectivePage, on_delete=models.CASCADE, related_name='images', null=False, blank=False)

    def save(self):
        super().save()

        img = Image.open(self.image)

        if img.height > 1000 or img.width > 1000:
            new_img = (1000, 1000)
            img.thumbnail(new_img)
            fh = storage.open(self.image.name, "w")
            img.save(fh, format='JPEG', quality=75)


@receiver(models.signals.post_delete, sender=DirectiveImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.name):
            os.remove(instance.image.name)


@receiver(models.signals.pre_save, sender=DirectiveImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = DirectiveImage.objects.get(pk=instance.pk).image
    except DirectiveImage.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
