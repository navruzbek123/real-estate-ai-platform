import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from pathlib import Path


class ModelTrainer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_dir = Path(__file__).parent
        self.model_path = self.model_dir / 'model.pkl'
        self.data_path = self.model_dir / 'training_data.csv'

    def generate_synthetic_data(self, num_samples=10000):
        np.random.seed(42)
        data = []

        cities = {
            'Москва': {'price_per_sqm': 350000, 'weight': 0.15},
            'Санкт-Петербург': {'price_per_sqm': 200000, 'weight': 0.10},
            'Московская область': {'price_per_sqm': 150000, 'weight': 0.08},
            'Новосибирск': {'price_per_sqm': 100000, 'weight': 0.06},
            'Екатеринбург': {'price_per_sqm': 95000, 'weight': 0.06},
            'Казань': {'price_per_sqm': 110000, 'weight': 0.05},
            'Нижний Новгород': {'price_per_sqm': 85000, 'weight': 0.05},
            'Челябинск': {'price_per_sqm': 65000, 'weight': 0.04},
            'Самара': {'price_per_sqm': 70000, 'weight': 0.04},
            'Омск': {'price_per_sqm': 60000, 'weight': 0.04},
            'Ростов-на-Дону': {'price_per_sqm': 75000, 'weight': 0.05},
            'Уфа': {'price_per_sqm': 68000, 'weight': 0.04},
            'Красноярск': {'price_per_sqm': 72000, 'weight': 0.04},
            'Пермь': {'price_per_sqm': 65000, 'weight': 0.04},
            'Воронеж': {'price_per_sqm': 68000, 'weight': 0.03},
            'Волгоград': {'price_per_sqm': 58000, 'weight': 0.03},
            'Краснодар': {'price_per_sqm': 95000, 'weight': 0.05},
            'Сочи': {'price_per_sqm': 180000, 'weight': 0.02},
        }

        city_names = list(cities.keys())
        city_weights = np.array([c['weight'] for c in cities.values()])
        city_weights = city_weights / city_weights.sum()

        for _ in range(num_samples):
            city = np.random.choice(city_names, p=city_weights)
            area = np.random.randint(20, 250)
            rooms = np.random.randint(1, 7)
            total_floors = np.random.randint(1, 30)
            floor = np.random.randint(1, total_floors + 1)
            home_type = np.random.choice(['apartment', 'house', 'townhouse'])

            base_price = cities[city]['price_per_sqm'] * area

            room_coef = 1 + (rooms - 1) * 0.05
            if floor == 1:
                floor_coef = 0.95
            elif floor == total_floors:
                floor_coef = 0.92
            else:
                floor_coef = 1.0

            if home_type == 'house':
                type_coef = 1.3
            elif home_type == 'townhouse':
                type_coef = 1.15
            else:
                type_coef = 1.0

            noise = np.random.uniform(0.85, 1.15)
            price = base_price * room_coef * floor_coef * type_coef * noise

            city_enc = list(cities.keys()).index(city) + 1
            type_enc = {'apartment': 0, 'house': 1, 'townhouse': 2}[home_type]

            data.append({
                'area': area,
                'rooms': rooms,
                'floor': floor,
                'total_floors': total_floors,
                'city_encoded': city_enc,
                'type_encoded': type_enc,
                'price': int(price)
            })

        return pd.DataFrame(data)

    def train(self):
        print("Генерация данных...")
        df = self.generate_synthetic_data(50000)

        X = df[['area', 'rooms', 'floor', 'total_floors', 'city_encoded', 'type_encoded']]
        y = df['price']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        print("Обучение модели...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)

        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"MAE: {mae:,.0f} руб.")
        print(f"R² Score: {r2:.4f}")

        self.save_model()
        print(f"Модель сохранена в {self.model_path}")
        return self.model

    def save_model(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)

    def load_model(self):
        if self.model_path.exists():
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data.get('model')
                self.scaler = data.get('scaler')
            return True
        return False


if __name__ == '__main__':
    trainer = ModelTrainer()
    trainer.train()
    print("Обучение завершено!")
