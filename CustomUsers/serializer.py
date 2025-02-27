from rest_framework import serializers


class SignupSerializer(serializers.Serializer):
    
    username = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    email= serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
    phone_number = serializers.CharField(max_length=100)
    profile_image = serializers.ImageField(required=False)

    def validate(self,data):

        if 'username' not in data:
            raise serializers.ValidationError({'details': 'Username is required'})
        if 'name' not in data:
            raise serializers.ValidationError({'details': 'Name is required'})
        if 'email' not in data:
            raise serializers.ValidationError({'details': 'Email is required'})
        if 'password' not in data:
            raise serializers.ValidationError({'details': 'Password is required'})
        if 'phone_number' not in data:
            raise serializers.ValidationError({'details': 'Phone number is required'})
        if len(data['password']) < 8:
            raise serializers.ValidationError({'details': 'Password must be at least 8 characters long'})
        return data
class LoginSerializer(serializers.Serializer):

    email = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        if 'email' not in data:
            raise serializers.ValidationError({'details': 'email is required'})
        if 'password' not in data:
            raise serializers.ValidationError({'details': 'Password is required'})
        
        return data