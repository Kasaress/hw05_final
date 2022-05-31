from django.utils import timezone


def year(request):
    return {
        'year': timezone.localtime(timezone.now()).year,
    }
