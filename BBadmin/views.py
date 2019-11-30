"""
Higher end admin views for frontend.
Stats from all over return per tab according to frontend organization
Will organise functions up top and pull them per info needed
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

