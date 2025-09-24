"""
Timezone Utilities Module
Provides timezone management functionality for the bot.
"""

import logging
import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

class TimezoneManager:
    def __init__(self):
        self.timezone_cache = {}
    
    async def get_timezone_for_city(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Get timezone information for a city"""
        try:
            # Check cache first
            if city_name.lower() in self.timezone_cache:
                return self.timezone_cache[city_name.lower()]
            
            # Use WorldTimeAPI for timezone detection
            timezone_info = await self._fetch_timezone_from_api(city_name)
            
            if timezone_info:
                # Cache the result
                self.timezone_cache[city_name.lower()] = timezone_info
                return timezone_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting timezone for city {city_name}: {e}")
            return None
    
    async def _fetch_timezone_from_api(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Fetch timezone information with robust fallback"""
        try:
            # Simple mapping for common cities (primary method - no API needed)
            city_timezone_mapping = {
                "москва": "Europe/Moscow",
                "санкт-петербург": "Europe/Moscow",
                "питер": "Europe/Moscow",
                "екатеринбург": "Asia/Yekaterinburg",
                "новосибирск": "Asia/Novosibirsk",
                "красноярск": "Asia/Krasnoyarsk",
                "иркутск": "Asia/Irkutsk",
                "владивосток": "Asia/Vladivostok",
                "хабаровск": "Asia/Vladivostok",
                "самара": "Europe/Samara",
                "казань": "Europe/Moscow",
                "нижний новгород": "Europe/Moscow",
                "челябинск": "Asia/Yekaterinburg",
                "омск": "Asia/Omsk",
                "ростов-на-дону": "Europe/Moscow",
                "уфа": "Asia/Yekaterinburg",
                "волгоград": "Europe/Moscow",
                "пермь": "Asia/Yekaterinburg",
                "краснодар": "Europe/Moscow",
                "саратов": "Europe/Moscow",
                "moscow": "Europe/Moscow",
                "saint petersburg": "Europe/Moscow",
                "new york": "America/New_York",
                "london": "Europe/London",
                "paris": "Europe/Paris",
                "berlin": "Europe/Berlin",
                "tokyo": "Asia/Tokyo",
                "beijing": "Asia/Shanghai",
                "sydney": "Australia/Sydney"
            }
            
            city_lower = city_name.lower().strip()
            timezone_name = city_timezone_mapping.get(city_lower, "Europe/Moscow")
            
            logger.info(f"Using timezone {timezone_name} for city {city_name}")
            
            # Return timezone info directly from mapping (no API call needed)
            return {
                "timezone": timezone_name,
                "offset": self._get_timezone_offset(timezone_name),
                "name": self._get_timezone_display_name(timezone_name),
                "city": city_name,
                "abbreviation": self._get_timezone_abbreviation(timezone_name)
            }
            
        except Exception as e:
            logger.error(f"Error processing timezone data: {e}")
            # Fallback to default
            return {
                "timezone": "Europe/Moscow",
                "offset": "+03:00",
                "name": "Московское время",
                "city": city_name,
                "abbreviation": "MSK"
            }
    
    def _get_timezone_display_name(self, timezone_name: str) -> str:
        """Get display name for timezone"""
        timezone_names = {
            "Europe/Moscow": "Московское время",
            "Asia/Yekaterinburg": "Екатеринбургское время",
            "Asia/Novosibirsk": "Новосибирское время",
            "Asia/Krasnoyarsk": "Красноярское время",
            "Asia/Irkutsk": "Иркутское время",
            "Asia/Vladivostok": "Владивостокское время",
            "Europe/Samara": "Самарское время",
            "Asia/Omsk": "Омское время",
            "America/New_York": "Восточное время (США)",
            "Europe/London": "Лондонское время",
            "Europe/Paris": "Парижское время",
            "Europe/Berlin": "Берлинское время",
            "Asia/Tokyo": "Токийское время",
            "Asia/Shanghai": "Пекинское время",
            "Australia/Sydney": "Сиднейское время"
        }
        
        return timezone_names.get(timezone_name, timezone_name)
    
    def _get_timezone_offset(self, timezone_name: str) -> str:
        """Get UTC offset for timezone"""
        timezone_offsets = {
            "Europe/Moscow": "+03:00",
            "Asia/Yekaterinburg": "+05:00",
            "Asia/Novosibirsk": "+07:00",
            "Asia/Krasnoyarsk": "+07:00",
            "Asia/Irkutsk": "+08:00",
            "Asia/Vladivostok": "+10:00",
            "Europe/Samara": "+04:00",
            "Asia/Omsk": "+06:00",
            "America/New_York": "-05:00",
            "Europe/London": "+00:00",
            "Europe/Paris": "+01:00",
            "Europe/Berlin": "+01:00",
            "Asia/Tokyo": "+09:00",
            "Asia/Shanghai": "+08:00",
            "Australia/Sydney": "+10:00"
        }
        
        return timezone_offsets.get(timezone_name, "+03:00")
    
    def _get_timezone_abbreviation(self, timezone_name: str) -> str:
        """Get timezone abbreviation"""
        timezone_abbreviations = {
            "Europe/Moscow": "MSK",
            "Asia/Yekaterinburg": "YEKT",
            "Asia/Novosibirsk": "NOVT",
            "Asia/Krasnoyarsk": "KRAT",
            "Asia/Irkutsk": "IRKT",
            "Asia/Vladivostok": "VLAT",
            "Europe/Samara": "SAMT",
            "Asia/Omsk": "OMST",
            "America/New_York": "EST",
            "Europe/London": "GMT",
            "Europe/Paris": "CET",
            "Europe/Berlin": "CET",
            "Asia/Tokyo": "JST",
            "Asia/Shanghai": "CST",
            "Australia/Sydney": "AEDT"
        }
        
        return timezone_abbreviations.get(timezone_name, "MSK")
    
    def get_user_local_time(self, user_timezone: str) -> datetime:
        """Get current time in user's timezone"""
        try:
            tz = pytz.timezone(user_timezone)
            return datetime.now(tz)
        except Exception as e:
            logger.error(f"Error getting local time for timezone {user_timezone}: {e}")
            return datetime.now(pytz.timezone("Europe/Moscow"))
    
    def is_comfortable_time(self, user_timezone: str, current_time: datetime = None) -> bool:
        """Check if current time is comfortable for messaging"""
        if current_time is None:
            current_time = self.get_user_local_time(user_timezone)
        
        hour = current_time.hour
        
        # Comfortable hours: 8-10, 12-14, 18-20
        return (8 <= hour <= 10) or (12 <= hour <= 14) or (18 <= hour <= 20)
    
    def get_next_comfortable_time(self, user_timezone: str) -> datetime:
        """Get next comfortable time for messaging"""
        current_time = self.get_user_local_time(user_timezone)
        
        # Define comfortable time slots
        comfortable_slots = [
            (8, 0),   # 8:00 AM
            (12, 0),  # 12:00 PM
            (18, 0)   # 6:00 PM
        ]
        
        for hour, minute in comfortable_slots:
            next_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has passed today, try tomorrow
            if next_time <= current_time:
                next_time += timedelta(days=1)
            
            return next_time
        
        # Fallback to tomorrow 8:00 AM
        return current_time.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def format_time_for_user(self, dt: datetime, user_timezone: str) -> str:
        """Format datetime for user's timezone"""
        try:
            tz = pytz.timezone(user_timezone)
            local_time = dt.astimezone(tz)
            return local_time.strftime("%H:%M %d.%m.%Y")
        except Exception as e:
            logger.error(f"Error formatting time: {e}")
            return dt.strftime("%H:%M %d.%m.%Y")
