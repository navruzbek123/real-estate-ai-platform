from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import Listing
from .yandex_maps import YandexMapsService
from realtors.models import Realtor


def index(request):
    listings = Listing.objects.filter(is_published=True, status='active').order_by('-is_premium', '-list_date')[:12]
    cities = Listing.objects.filter(is_published=True, status='active').values_list('city', flat=True).distinct()
    context = {'listings': listings, 'cities': cities}
    return render(request, 'index.html', context)


def listings(request):
    listings = Listing.objects.filter(is_published=True, status='active').order_by('-is_premium', '-list_date')
    paginator = Paginator(listings, 12)
    page = request.GET.get('page')
    listings_page = paginator.get_page(page)
    context = {'listings': listings_page, 'count': listings.count()}
    return render(request, 'listings/listings.html', context)


def listing_detail(request, slug):
    listing = get_object_or_404(Listing, slug=slug, is_published=True)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = request.user.favorites.filter(listing=listing).exists()
    related = Listing.objects.filter(city=listing.city, is_published=True, status='active').exclude(id=listing.id)[:3]
    context = {'listing': listing, 'is_favorite': is_favorite, 'related_listings': related}
    return render(request, 'listings/listing_detail.html', context)


def search(request):
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    bedrooms = request.GET.get('bedrooms', '')
    
    listings = Listing.objects.filter(is_published=True, status='active')
    
    if query:
        listings = listings.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query))
    if city:
        listings = listings.filter(city__icontains=city)
    if bedrooms:
        listings = listings.filter(bedrooms__gte=int(bedrooms))
    
    listings = listings.order_by('-is_premium', '-list_date')
    paginator = Paginator(listings, 12)
    page = request.GET.get('page')
    listings_page = paginator.get_page(page)
    
    context = {'listings': listings_page, 'count': listings.count(), 'query': query, 'city': city, 'bedrooms': bedrooms}
    return render(request, 'listings/search.html', context)


@login_required
def create_listing(request):
    if request.user.has_reached_listing_limit(request.user.listings.count()):
        messages.error(request, 'Вы достигли лимита объявлений')
        return redirect('profile')
    
    if request.method == 'POST':
        slug = f"{request.POST.get('title', '').lower().replace(' ', '-')[:50]}-{request.user.id}"
        listing = Listing.objects.create(
            user=request.user,
            realtor=Realtor.objects.first() or Realtor.objects.create(name='Admin', email='admin@test.ru', phone='123'),
            slug=slug,
            title=request.POST.get('title'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state', ''),
            zipcode=request.POST.get('zipcode', ''),
            description=request.POST.get('description', ''),
            sale_type=request.POST.get('sale_type', 'For Sale'),
            price=request.POST.get('price', 0),
            bedrooms=request.POST.get('bedrooms', 1),
            bathrooms=request.POST.get('bathrooms', 1),
            home_type=request.POST.get('home_type', 'Condo'),
            sqft=request.POST.get('sqft', 50),
        )
        messages.success(request, 'Объявление создано!')
        return redirect('listing-detail', slug=listing.slug)
    
    return render(request, 'listings/create.html')


class ListingsView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        listings = Listing.objects.filter(is_published=True).order_by('-list_date')
        paginator = Paginator(listings, 3)
        page = request.GET.get('page', 1)
        listings_page = paginator.get_page(page)
        
        data = [{
            'id': l.id, 'title': l.title, 'slug': l.slug, 'city': l.city,
            'price': l.price, 'bedrooms': l.bedrooms, 'sqft': l.sqft,
            'photo_main': l.photo_main.url if l.photo_main else None,
            'listing_url': f'/listings/{l.slug}/',
        } for l in listings_page]
        
        return Response({'listings': data, 'page': page, 'has_next': listings_page.has_next()})


class ListingView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request, slug):
        try:
            l = Listing.objects.get(slug=slug)
        except Listing.DoesNotExist:
            return Response({'error': 'Не найдено'}, status=404)
        
        return Response({
            'id': l.id, 'title': l.title, 'slug': l.slug, 'address': l.address,
            'city': l.city, 'price': l.price, 'bedrooms': l.bedrooms,
            'bathrooms': str(l.bathrooms), 'sqft': l.sqft, 'description': l.description,
            'photo_main': l.photo_main.url if l.photo_main else None,
        })


class SearchView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        keywords = request.data.get('keywords', '')
        listings = Listing.objects.filter(is_published=True)
        
        if keywords:
            listings = listings.filter(Q(title__icontains=keywords) | Q(description__icontains=keywords))
        
        data = [{
            'id': l.id, 'title': l.title, 'slug': l.slug, 'city': l.city,
            'price': l.price, 'photo_main': l.photo_main.url if l.photo_main else None,
        } for l in listings[:12]]
        
        return Response({'listings': data})


class MapListingsView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        city = request.GET.get('city', '')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        min_bedrooms = request.GET.get('min_bedrooms')
        bedrooms = request.GET.get('bedrooms')
        
        listings = Listing.objects.filter(is_published=True, status='active', latitude__isnull=False, longitude__isnull=False)
        
        if city:
            listings = listings.filter(city__icontains=city)
        if min_price:
            listings = listings.filter(price__gte=int(min_price))
        if max_price:
            listings = listings.filter(price__lte=int(max_price))
        if bedrooms:
            listings = listings.filter(bedrooms__gte=int(bedrooms))
        
        data = [{
            'id': l.id,
            'title': l.title,
            'slug': l.slug,
            'address': l.address,
            'city': l.city,
            'price': l.price,
            'bedrooms': l.bedrooms,
            'sqft': l.sqft,
            'latitude': l.latitude,
            'longitude': l.longitude,
            'is_premium': l.is_premium,
            'photo_main': l.photo_main.url if l.photo_main else None,
            'listing_url': f'/listings/{l.slug}/',
        } for l in listings[:100]]
        
        return Response({'listings': data})


class GeocodeView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        address = request.data.get('address', '')
        if not address or not address.strip():
            return Response({'error': 'Address required'}, status=400)
        
        result = YandexMapsService.geocode(address.strip())
        if result:
            return Response(result)
        return Response({'error': 'Geocoding failed'}, status=400)


class UpdateListingCoordsView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request, slug):
        try:
            listing = Listing.objects.get(slug=slug)
        except Listing.DoesNotExist:
            return Response({'error': 'Listing not found'}, status=404)
        
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        
        if lat and lng:
            listing.latitude = float(lat)
            listing.longitude = float(lng)
            listing.save()
            return Response({'success': True, 'latitude': lat, 'longitude': lng})
        
        full_address = f"{listing.address}, {listing.city}, {listing.state} {listing.zipcode}"
        coords = YandexMapsService.geocode(full_address)
        
        if coords:
            listing.latitude = coords['latitude']
            listing.longitude = coords['longitude']
            listing.save()
            return Response({'success': True, **coords})
        
        return Response({'error': 'Could not geocode address'}, status=400)
