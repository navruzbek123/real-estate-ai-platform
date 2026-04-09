from django.urls import path
from .views import ListingsView, ListingView, SearchView, MapListingsView, GeocodeView, UpdateListingCoordsView

urlpatterns = [
    path('', ListingsView.as_view(), name='api-listings'),
    path('search', SearchView.as_view(), name='api-search'),
    path('map/', MapListingsView.as_view(), name='api-map-listings'),
    path('geocode/', GeocodeView.as_view(), name='api-geocode'),
    path('<slug:slug>', ListingView.as_view(), name='api-listing-detail'),
    path('<slug:slug>/coords/', UpdateListingCoordsView.as_view(), name='api-update-coords'),
]
