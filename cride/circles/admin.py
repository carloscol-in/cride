"""Circles admin."""

# Python
import csv
from datetime import timedelta, datetime

# Django 
from django.contrib import admin
from django.utils import timezone
from django.http import HttpResponse

# Models
from cride.rides.models import Ride
from cride.circles.models import Circle

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """Circle admin."""

    list_display = (
        'slug_name',
        'name',
        'is_public',
        'verified',
        'is_limited',
        'members_limit',
    )
    search_fields = ('slug_name', 'name')
    list_filter = (
        'is_public',
        'verified',
        'is_limited',
    )

    actions = ['unverify_circles', 'verify_circles', 'download_todays_rides']

    def unverify_circles(self, request, queryset):
        """Make circles verified."""
        queryset.update(verified=False)
    unverify_circles.short_description = 'Make selected circles not verified'

    def verify_circles(self, request, queryset):
        """Make circles verified."""
        queryset.update(verified=True)
    verify_circles.short_description = 'Make selected circles verified'

    def download_todays_rides(self, request, queryset):
        """Return today's rides."""
        now = timezone.now()
        start = datetime(now.year, now.month, now.day, 0, 0, 0)
        end = start + timedelta(days=1)
        rides_today = Ride.objects.filter(
            offered_in__in=queryset.values_list('id'),
            departure_date__gte=start,
            departure_date__lte=end
        ).order_by('departure_date')

        # import pdb;pdb.set_trace()

        response = HttpResponse(content_type='text/csv')

        if len(queryset) == 1:
            response['Content-Disposition'] = f'attachment; filename="{start.strftime("%Y-%m-%d")}_rides--{queryset[0].slug_name}.csv"'
        elif len(queryset) > 1:
            response['Content-Disposition'] = f'attachment; filename="{start.strftime("%Y-%m-%d")}_rides.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'id', 'passengers', 'departure_location',
            'departure_date', 'arrival_location',
            'arrival_date', 'rating',
        ])
        for ride in rides_today:
            writer.writerow([
                ride.pk,
                ride.passengers.count(),
                ride.departure_location,
                str(ride.departure_date),
                ride.arrival_location,
                str(ride.arrival_date),
                ride.rating,
            ])
        return response
    download_todays_rides.short_description = 'Download today\'s rides in CSV'