# authentication.py
import ast
import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions

User = get_user_model()
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

class RedisSessionAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        print("=== REDIS AUTHENTICATION DEBUG ===")
        session_id = request.COOKIES.get('session_id')
        print(f"Session ID from cookies: {session_id}")
        print(f"All cookies: {request.COOKIES}")
        
        if not session_id:
            print("❌ No session_id in cookies")
            return None
        
        try:
            session_data_bytes = session_storage.get(session_id)
            print(f"Session data from Redis: {session_data_bytes}")
            
            if not session_data_bytes:
                print("❌ No session data in Redis")
                return None
                
            session_data = ast.literal_eval(session_data_bytes.decode('utf-8'))
            user_id = session_data.get('user_id')
            
            print(f"Session data parsed: {session_data}")
            print(f"User ID from session: {user_id}")
            
            if not user_id:
                print("❌ No user_id in session data")
                return None
                
            try:
                user = User.objects.get(id=user_id)
                print(f"✅ User found: {user.email}, is_superuser: {user.is_superuser}")
                return (user, None)
            except User.DoesNotExist:
                print(f"❌ User with id {user_id} does not exist")
                return None
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None