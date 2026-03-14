import json
import os
import re
from datetime import datetime, timedelta


class LegacyRoomService:
    def __init__(self, next_rooms_path, next_room_slug_by_number, month_labels_ru, high_season_month_keys):
        self.next_rooms_path = next_rooms_path
        self.next_room_slug_by_number = next_room_slug_by_number
        self.month_labels_ru = month_labels_ru
        self.high_season_month_keys = set(high_season_month_keys)
        self._next_rooms_cache = None

    def get_room_price_for_month(self, room, month_name=None):
        if month_name is None:
            month_name = datetime.now().strftime('%B')

        prices = room.price_per_night
        if isinstance(prices, str):
            prices = json.loads(prices)

        return prices.get(month_name)

    def get_room_max_capacity(self, room):
        max_capacity = room.capacity
        if room.has_small_sofa:
            max_capacity += 1
        if room.has_large_sofa:
            max_capacity += 2
        return max_capacity

    def get_room_prices(self, room):
        prices = room.price_per_night
        if isinstance(prices, str):
            prices = json.loads(prices)
        return prices

    def get_plain_text(self, value):
        if not value:
            return ''
        plain_text = re.sub(r'<[^>]+>', ' ', value)
        return re.sub(r'\s+', ' ', plain_text).strip()

    def load_next_rooms_data(self):
        if self._next_rooms_cache is None:
            if not os.path.exists(self.next_rooms_path):
                self._next_rooms_cache = []
            else:
                with open(self.next_rooms_path, 'r', encoding='utf-8') as file:
                    self._next_rooms_cache = json.load(file)
        return self._next_rooms_cache

    def get_next_room_by_slug(self, slug):
        return next((room for room in self.load_next_rooms_data() if room.get('slug') == slug), None)

    def get_next_room_by_number(self, number):
        slug = self.next_room_slug_by_number.get((number or '').upper())
        if not slug:
            return None
        return self.get_next_room_by_slug(slug)

    def get_room_type_slug(self, room):
        room_type_slug = getattr(room, 'room_type_slug', None)
        if room_type_slug:
            return room_type_slug
        return self.next_room_slug_by_number.get((getattr(room, 'number', '') or '').upper())

    def get_next_room_by_room(self, room):
        slug = self.get_room_type_slug(room)
        if not slug:
            return None
        return self.get_next_room_by_slug(slug)

    def get_next_room_feature_labels(self, room):
        features = room.get('features', {})
        labels = []
        if features.get('seaView'):
            labels.append('Вид на море')
        if features.get('balcony'):
            labels.append('Балкон')
        if features.get('terrace'):
            labels.append('Терраса')
        if features.get('accessible'):
            labels.append('Доступно для МГН')
        if features.get('firstFloor'):
            labels.append('Первый этаж')
        if features.get('kitchen'):
            labels.append('Кухня')
        return labels

    def get_next_room_price_bands(self, room):
        prices = room.get('prices', [])
        low_prices = [item['price'] for item in prices if item.get('month') not in {'Июнь', 'Июль', 'Август', 'Сентябрь'}]
        high_prices = [item['price'] for item in prices if item.get('month') in {'Июнь', 'Июль', 'Август', 'Сентябрь'}]
        return {
            'low': min(low_prices) if low_prices else room.get('minPrice', 0),
            'high': min(high_prices) if high_prices else room.get('maxPrice', 0),
        }

    def build_next_room_card_data(self, room, detail_url):
        price_bands = self.get_next_room_price_bands(room)
        return {
            'id': room.get('id'),
            'name': room.get('name'),
            'category': room.get('category'),
            'category_group': room.get('category'),
            'short_description': room.get('shortDescription'),
            'feature_labels': self.get_next_room_feature_labels(room),
            'area': room.get('area', 0),
            'area_label': f"{room.get('area')} м²" if room.get('area') else None,
            'max_capacity': room.get('capacity', {}).get('max', 0),
            'high_season_price': price_bands['high'],
            'low_season_price': price_bands['low'],
            'min_price': room.get('minPrice', price_bands['low']),
            'max_price': room.get('maxPrice', price_bands['high']),
            'price_sort': price_bands['low'] or room.get('minPrice', 0),
            'photo_url': room.get('heroImage'),
            'detail_url': detail_url,
        }

    def get_next_room_monthly_price_items(self, room):
        prices = {item['month']: item['price'] for item in room.get('prices', [])}
        current_month_key = self.month_labels_ru[datetime.now().month - 1][0]
        items = []
        for month_key, label in self.month_labels_ru:
            items.append({
                'key': month_key,
                'label': label,
                'price': prices.get(label, room.get('minPrice', 0)),
                'is_current': month_key == current_month_key,
                'tier': self.get_month_heatmap_tier(month_key),
            })
        return items

    def get_month_heatmap_tier(self, month_key):
        if month_key in {'January', 'February', 'March', 'April', 'November', 'December'}:
            return 'cold'
        if month_key == 'May':
            return 'growth'
        if month_key in {'June', 'October'}:
            return 'warm'
        if month_key in {'July', 'September'}:
            return 'high'
        if month_key == 'August':
            return 'peak'
        return 'cold'

    def get_room_category_group_from_name(self, name):
        value = (name or '').lower()
        if 'апартамент' in value:
            return 'Апартаменты'
        if 'deluxe' in value or 'делюкс' in value:
            return 'Deluxe'
        return 'Стандарт'

    def get_room_display_name(self, room):
        next_room = self.get_next_room_by_room(room)
        if next_room and next_room.get('name'):
            return next_room['name']
        return room.category.name if room.category else f'Номер {room.number}'

    def get_room_display_category(self, room):
        next_room = self.get_next_room_by_room(room)
        if next_room and next_room.get('category'):
            return next_room['category']
        return room.category.name if room.category else 'Номер'

    def infer_room_area(self, room):
        text = ' '.join(filter(None, [
            self.get_room_display_name(room),
            self.get_plain_text(room.description),
            self.get_plain_text(room.amenities),
        ]))
        match = re.search(r'(\d{2,3})\s*(?:м2|м²|кв\.?\s*м|кв\.?\s*метр)', text, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def get_room_short_description(self, room):
        plain = self.get_plain_text(room.description)
        if not plain:
            return 'Комфортный номер у моря в Таласса Hotel & Spa.'

        first_sentence = re.split(r'(?<=[.!?])\s+', plain, maxsplit=1)[0].strip()
        text = first_sentence or plain
        if len(text) <= 190:
            return text

        shortened = text[:190].rsplit(' ', 1)[0].strip()
        return f'{shortened}...'

    def get_room_amenities_list(self, room):
        raw = room.amenities
        if not raw:
            return []

        if isinstance(raw, list):
            values = raw
        elif isinstance(raw, dict):
            values = list(raw.values())
        else:
            stripped = str(raw).strip()
            if not stripped:
                return []
            try:
                parsed = json.loads(stripped)
            except (json.JSONDecodeError, TypeError):
                parsed = None

            if isinstance(parsed, list):
                values = parsed
            elif isinstance(parsed, dict):
                values = list(parsed.values())
            else:
                plain = self.get_plain_text(stripped)
                normalized = plain.replace('•', '\n').replace('·', '\n').replace(';', '\n').replace(',', '\n')
                values = normalized.split('\n')

        items = []
        for value in values:
            extracted_values = [value]
            if isinstance(value, str):
                nested = value.strip()
                if nested.startswith('[') and nested.endswith(']'):
                    try:
                        parsed_nested = json.loads(nested)
                    except (json.JSONDecodeError, TypeError):
                        parsed_nested = None
                    if isinstance(parsed_nested, list):
                        extracted_values = parsed_nested

            for extracted in extracted_values:
                clean = self.get_plain_text(str(extracted)).strip(' -[]"\'')
                if not clean:
                    continue

                for chunk in clean.replace('•', '\n').replace('·', '\n').split('\n'):
                    normalized_chunk = chunk.strip(' -[]"\'')
                    if normalized_chunk:
                        items.append(normalized_chunk)

        return list(dict.fromkeys(items))

    def get_room_feature_labels(self, room):
        haystack = ' '.join(filter(None, [
            self.get_room_display_name(room),
            self.get_plain_text(room.description),
            ' '.join(self.get_room_amenities_list(room)),
        ])).lower()

        features = []
        if 'вид на море' in haystack:
            features.append('Вид на море')
        if 'балкон' in haystack:
            features.append('Балкон')
        if 'террас' in haystack:
            features.append('Терраса')
        if any(keyword in haystack for keyword in ['мгн', 'адапт', 'доступ', 'коляск', 'инвалид']):
            features.append('Доступно для МГН')
        if 'первый этаж' in haystack or re.search(r'\b1\s*этаж', haystack):
            features.append('Первый этаж')
        if 'кухн' in haystack:
            features.append('Кухня')
        return features

    def get_room_extra_bed_label(self, room):
        if room.has_large_sofa:
            return 'раскладной диван'
        if room.has_small_sofa:
            return 'кресло-кровать'
        return None

    def get_room_price_bands(self, room):
        prices = self.get_room_prices(room)
        low_prices = [price for month, price in prices.items() if month not in self.high_season_month_keys]
        high_prices = [price for month, price in prices.items() if month in self.high_season_month_keys]
        all_prices = [price for _, price in prices.items()]
        return {
            'low': min(low_prices) if low_prices else (min(all_prices) if all_prices else 0),
            'high': min(high_prices) if high_prices else (max(all_prices) if all_prices else 0),
            'min': min(all_prices) if all_prices else 0,
            'max': max(all_prices) if all_prices else 0,
        }

    def build_legacy_room_card_data(self, room, detail_url, photo_url):
        price_bands = self.get_room_price_bands(room)
        area = self.infer_room_area(room)
        display_name = self.get_room_display_name(room)
        return {
            'id': room.id,
            'name': display_name,
            'category': self.get_room_display_category(room),
            'category_group': self.get_room_category_group_from_name(display_name),
            'short_description': self.get_room_short_description(room),
            'feature_labels': self.get_room_feature_labels(room),
            'area': area or 0,
            'area_label': f'{area} м²' if area else None,
            'capacity': room.capacity,
            'max_capacity': self.get_room_max_capacity(room),
            'high_season_price': price_bands['high'],
            'low_season_price': price_bands['low'],
            'min_price': price_bands['min'],
            'max_price': price_bands['max'],
            'price_sort': price_bands['low'] or price_bands['min'],
            'photo_url': photo_url,
            'detail_url': detail_url,
        }

    def get_monthly_price_items(self, room):
        prices = self.get_room_prices(room)
        current_month = datetime.now().strftime('%B')
        items = []
        for month_key, month_label in self.month_labels_ru:
            items.append({
                'key': month_key,
                'label': month_label,
                'price': prices.get(month_key, 0),
                'is_current': month_key == current_month,
            })
        return items

    def calculate_room_total_price(self, room, check_in, check_out, adults, children, children_under_five=0, is_high_season=None):
        if is_high_season is None:
            is_high_season = self.is_high_season

        prices = self.get_room_prices(room)
        base_price = 0
        current_date = check_in
        while current_date < check_out:
            base_price += prices[current_date.strftime('%B')]
            current_date += timedelta(days=1)

        total_price = base_price
        extra_price = 0
        total_guests = adults + children
        base_capacity = room.capacity

        if total_guests > base_capacity:
            extra_guests = total_guests - base_capacity
            extra_children = min(children, extra_guests)
            remaining_extra = extra_guests - extra_children
            extra_adults = min(adults, remaining_extra)

            current_date = check_in
            while current_date < check_out:
                if is_high_season(current_date):
                    adult_extra_price = 2500
                    child_extra_price = 1500
                else:
                    adult_extra_price = 2000
                    child_extra_price = 1000

                extra_price += (extra_adults * adult_extra_price) + (extra_children * child_extra_price)
                current_date += timedelta(days=1)

            total_price += extra_price

        return {
            'total': total_price,
            'base_price': base_price,
            'extra_price': extra_price,
            'nights': (check_out - check_in).days,
        }

    def build_booking_result_data(self, room, total_info, photo_url, book_url):
        return {
            'id': room.id,
            'number': room.number,
            'name': self.get_room_display_name(room),
            'category_name': self.get_room_display_category(room),
            'photo_url': photo_url,
            'capacity': room.capacity,
            'max_capacity': self.get_room_max_capacity(room),
            'nights': total_info['nights'] if total_info else None,
            'total_price': total_info['total'] if total_info else self.get_room_price_for_month(room),
            'base_price': total_info['base_price'] if total_info else None,
            'extra_price': total_info['extra_price'] if total_info else None,
            'price_caption': f"за {total_info['nights']} ноч." if total_info else 'за ночь в текущем месяце',
            'book_url': book_url,
        }

    def normalize_rooms_highlights(self, items=None):
        fallback_highlights = [
            'Отель в 30 метрах от моря с собственным пляжем (шезлонги, зонтики и пляжные полотенца входят в стоимость номера)',
            'Подогреваемый бассейн',
            'Оздоровительные процедуры',
            'Приморский ресторанчик с русской, европейской и национальной кухнями. Завтраки включены с июня по октябрь',
            'Шустрый WiFi',
            'Своя территория с парковкой',
            'Стильные уютные интерьеры для комфортного отдыха',
        ]
        if not items:
            return fallback_highlights

        normalized = []
        for item in items:
            if not item:
                continue
            text = str(item).strip()
            if text == 'Стильные уютные интерьеры не только для фото, а для комфортного отдыха':
                text = 'Стильные уютные интерьеры для комфортного отдыха'
            if text not in normalized:
                normalized.append(text)

        if not normalized:
            return fallback_highlights

        result = [item for item in normalized if item != 'Шустрый WiFi']
        restaurant_text = 'Приморский ресторанчик с русской, европейской и национальной кухнями. Завтраки включены с июня по октябрь'
        if restaurant_text in result:
            restaurant_index = result.index(restaurant_text)
            result.insert(restaurant_index + 1, 'Шустрый WiFi')
        elif 'Шустрый WiFi' not in result:
            result.append('Шустрый WiFi')
        return result

