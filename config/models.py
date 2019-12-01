# from xml.dom import minidom
# from django.db import models
# from model_utils import Choices

# class UserTypeStatic(models.Model):
#     '''
#     Serves pictures and descriptions etc. to inform user of usertypes on landing page
#     '''

#     label = models.CharField(max_length=20, unique=True)
#     short_description = models.CharField(max_length=150, blank=True, null=True)
#     display_image = models.ImageField(max_length=1000, upload_to='misc/', blank=True, null=True)
#     tagline = models.CharField(max_length=300, blank=True, null=True)
#     full_text = models.TextField(blank=True, null=True)
