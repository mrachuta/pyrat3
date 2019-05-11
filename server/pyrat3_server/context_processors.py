from .models import Client


# Return to each template, how much clients are associated with server
def count_associated_clients(request):
    return {
        'associated_clients_count': Client.objects.all().count()
    }