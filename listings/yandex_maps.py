import requests
from django.conf import settings


class YandexMapsService:
    GEOCODER_URL = 'https://geocode-maps.yandex.ru/1.x/'
    API_KEY = '488b5b96-5d6b-4664-8bdb-76ef7016822f'
    
    @classmethod
    def geocode(cls, address):
        if not address:
            return None
        
        api_key = getattr(settings, 'YANDEX_MAPS_API_KEY', '') or cls.API_KEY
        
        params = {
            'geocode': address,
            'format': 'json',
        }
        if api_key:
            params['apikey'] = api_key
        
        try:
            response = requests.get(cls.GEOCODER_URL, params=params, timeout=10)
            data = response.json()
            
            response_meta = data.get('response', {}).get('GeoObjectCollection', {})
            feature_members = response_meta.get('featureMember', [])
            
            if feature_members:
                point = feature_members[0]['GeoObject']['Point']['pos']
                longitude, latitude = point.split()
                return {
                    'latitude': float(latitude),
                    'longitude': float(longitude),
                }
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return None
    
    @classmethod
    def get_address_from_coords(cls, latitude, longitude):
        api_key = getattr(settings, 'YANDEX_MAPS_API_KEY', '') or cls.API_KEY
        
        params = {
            'geocode': f'{longitude},{latitude}',
            'format': 'json',
            'kind': 'house',
        }
        if api_key:
            params['apikey'] = api_key
        
        try:
            response = requests.get(cls.GEOCODER_URL, params=params, timeout=10)
            data = response.json()
            
            response_meta = data.get('response', {}).get('GeoObjectCollection', {})
            feature_members = response_meta.get('featureMember', [])
            
            if feature_members:
                geo_object = feature_members[0]['GeoObject']
                return {
                    'full_address': geo_object.get('metaDataProperty', {}).get('GeocoderMetaData', {}).get('text', ''),
                    'kind': geo_object.get('metaDataProperty', {}).get('GeocoderMetaData', {}).get('kind', ''),
                }
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
        
        return None


def geocode_address(address):
    return YandexMapsService.geocode(address)
