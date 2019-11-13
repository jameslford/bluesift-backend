'''
BBAdmin is an alias for static content.
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
    TYPES = Choices('Analytics', 'Projects', 'Locations', 'Profile', 'Company_Info')
    label = models.CharField(choices=TYPES, max_length=18, unique=True)
    description = models.CharField(max_length=60, blank=True, null=True)
    draw_path = models.TextField(blank=True, null=True)
    display = models.FileField(upload_to='misc/')
    for_user = models.BooleanField(default=False)
    for_pro = models.BooleanField(default=False)
    for_supplier = models.BooleanField(default=False)

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.display:
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

# class UserTypeStatic(models.Model):
#     '''
#     Serves pictures and descriptions etc. to inform user of usertypes on landing page
#     '''

#     label = models.CharField(max_length=20)
#     short_description = models.CharField(max_length=150)
#     display_image = models.ImageField(max_length=1000, upload_to='misc/')

