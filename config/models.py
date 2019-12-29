'''
These models hold/relay static materials served for front end
'''

from xml.dom import minidom
from django.db import models
from model_utils import Choices

class LibraryLink(models.Model):
    '''
    Holds svg paths (draw_path), descriptions and labels for user libraries.
    uses for_user/retailer/pro to serve the correct links per user accordingly
    '''
    TYPES = Choices('Analytics', 'Projects', 'Locations', 'Profile', 'Company_Info', 'Admin', 'Dashboard')
    label = models.CharField(choices=TYPES, max_length=18, unique=True)
    description = models.CharField(max_length=60, blank=True, null=True)
    draw_path = models.TextField(blank=True, null=True)
    display = models.FileField(upload_to='misc/', blank=True, null=True)
    for_user = models.BooleanField(default=False)
    for_pro = models.BooleanField(default=False)
    for_supplier = models.BooleanField(default=False)
    for_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.display:
            super().save(*args, **kwargs)
            return
        o_file = self.display
        doc = minidom.parse(o_file)
        paths = doc.getElementsByTagName('path')
        for path in paths:
            path_id = path.getAttribute('id')
            if path_id == 'drawPath':
                self.draw_path = path.getAttribute('d')
                break
        super().save(*args, **kwargs)


    def serialize(self):
        return {
            'label': self.label,
            'image': self.draw_path,
            'description': self.description
            }

class UserFeature(models.Model):
    label = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=60, blank=True, null=True)
    draw_path = models.TextField(blank=True, null=True)
    display = models.FileField(upload_to='misc/', blank=True, null=True)

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.display:
            super().save(*args, **kwargs)
            return
        o_file = self.display
        doc = minidom.parse(o_file)
        paths = doc.getElementsByTagName('path')
        for path in paths:
            path_id = path.getAttribute('id')
            if path_id == 'drawPath':
                self.draw_path = path.getAttribute('d')
                break
        super().save(*args, **kwargs)

    def serialize(self):
        return {
            'label': self.label,
            'description': self.description,
            'draw_path': self.draw_path
        }


class UserTypeStatic(models.Model):
    '''
    Serves pictures and descriptions etc. to inform user of usertypes on landing page
    '''

    label = models.CharField(max_length=20, unique=True)
    short_description = models.CharField(max_length=150, blank=True, null=True)
    display_image = models.ImageField(max_length=1000, upload_to='misc/', blank=True, null=True)
    tagline = models.CharField(max_length=300, blank=True, null=True)
    full_text = models.TextField(blank=True, null=True)
    feature = models.ManyToManyField(UserFeature, related_name='ut_static', blank=True)
    include_options = models.BooleanField(default=False)

    def __str__(self):
        return self.label

    def serialize(self):
        return {
            'label': self.label,
            'short_description': self.short_description,
            'image': self.display_image.url if self.display_image else None,
            'tagline': self.tagline,
            'full_text': self.full_text,
            'features': [feat.serialize() for feat in self.feature.all()],
            'options': ['owner', 'admin', 'employee'] if self.include_options else None
        }
