import os
import pickle
import numpy as np
from pathlib import Path


class PricePredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = ['area', 'rooms', 'floor', 'total_floors', 'city_encoded', 'type_encoded']
        self.model_path = Path(__file__).parent / 'model.pkl'
        self._load_model()

    def _load_model(self):
        if self.model_path.exists():
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data.get('model')
                    self.scaler = data.get('scaler')
            except Exception as e:
                print(f"Ошибка загрузки модели: {e}")
                self.model = None
                self.scaler = None

    def _get_city_encoding(self, city):
        city_map = {
            'Москва': 10, 'Санкт-Петербург': 9, 'Новосибирск': 8,
            'Екатеринбург': 7, 'Казань': 7, 'Нижний Новгород': 6,
            'Челябинск': 6, 'Самара': 6, 'Омск': 5, 'Ростов-на-Дону': 6,
            'Уфа': 6, 'Красноярск': 6, 'Пермь': 5, 'Воронеж': 5,
            'Волгоград': 5, 'Краснодар': 7, 'Сочи': 8,
            'Московская область': 7, 'Ленинградская область': 5
        }
        return city_map.get(city, 5)

    def _get_type_encoding(self, home_type):
        type_map = {
            'Condo': 0, 'apartment': 0, 'Квартира': 0,
            'House': 1, 'Дом': 1,
            'Townhouse': 2, 'Таунхаус': 2
        }
        return type_map.get(home_type, 0)

    def _get_floor_coefficient(self, floor, total_floors):
        if total_floors == 0:
            total_floors = 5
        if floor == 1:
            return 0.95
        elif floor == total_floors:
            return 0.92
        elif floor > total_floors:
            return 0.90
        else:
            mid = total_floors / 2
            if abs(floor - mid) < 1:
                return 1.05
            return 1.0

    def predict(self, area, rooms, city, floor, total_floors, home_type):
        if self.model is None:
            return self._estimate_fallback(area, rooms, city, floor, total_floors, home_type)

        try:
            city_enc = self._get_city_encoding(city)
            type_enc = self._get_type_encoding(home_type)
            floor_coef = self._get_floor_coefficient(floor, total_floors)

            features = np.array([[area, rooms, floor, total_floors, city_enc, type_enc]])

            if self.scaler:
                features = self.scaler.transform(features)

            price = self.model.predict(features)[0]
            price = price * floor_coef

            min_price = area * 50000
            max_price = area * 500000
            price = max(min_price, min(price, max_price))

            confidence = 0.85
            if abs(price - min_price) < (max_price - min_price) * 0.1:
                confidence = 0.70
            elif abs(price - max_price) < (max_price - min_price) * 0.1:
                confidence = 0.75

            return {
                'price': int(price),
                'price_per_sqm': int(price / area) if area > 0 else 0,
                'confidence': confidence,
                'floor_coefficient': floor_coef,
                'city_encoded': city_enc,
                'type_encoded': type_enc
            }

        except Exception as e:
            print(f"Ошибка предсказания: {e}")
            return self._estimate_fallback(area, rooms, city, floor, total_floors, home_type)

    def _estimate_fallback(self, area, rooms, city, floor, total_floors, home_type):
        base_prices = {
            'Москва': 350000, 'Санкт-Петербург': 200000, 'Новосибирск': 100000,
            'Екатеринбург': 95000, 'Казань': 110000, 'Нижний Новгород': 85000,
            'Челябинск': 65000, 'Самара': 70000, 'Омск': 60000,
            'Ростов-на-Дону': 75000, 'Уфа': 68000, 'Красноярск': 72000,
            'Пермь': 65000, 'Воронеж': 68000, 'Волгоград': 58000,
            'Краснодар': 95000, 'Сочи': 180000,
            'Московская область': 150000, 'Ленинградская область': 90000
        }

        base_price = base_prices.get(city, 80000)
        room_multiplier = 1 + (rooms - 1) * 0.05
        floor_coef = self._get_floor_coefficient(floor, total_floors)

        if home_type in ['House', 'Дом']:
            base_price *= 1.3

        price = area * base_price * room_multiplier * floor_coef

        return {
            'price': int(price),
            'price_per_sqm': int(price / area) if area > 0 else base_price,
            'confidence': 0.75,
            'floor_coefficient': floor_coef,
            'city_encoded': self._get_city_encoding(city),
            'type_encoded': self._get_type_encoding(home_type)
        }


predictor = PricePredictor()


def estimate_price(area, rooms, city, floor, total_floors, home_type):
    return predictor.predict(area, rooms, city, floor, total_floors, home_type)
