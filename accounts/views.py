import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User
from .utils import verify_business_number
from store.models import Store


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)

        user_role = 'owner' if user.is_owner else 'user'
        
        display_name = user.nickname if user.nickname else user.username

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'nickname': display_name,
            'role': user_role,
            'username': user.username
        }, status=200)
    else:
        return Response({"error": "아이디 또는 비밀번호가 틀렸습니다."}, status=401)

# 사업자번호 유효 검증 api
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_biz(request):
    b_no = request.data.get('business_number', '').replace('-', '').strip()
    
    if not b_no or len(b_no) != 10:
        return Response({"error": "10자리 사업자 번호를 입력해주세요."}, status=400)
    
    if User.objects.filter(business_number=b_no).exists():
        return Response({"error": "이미 가입된 사업자 번호입니다."}, status=400)

    is_valid, status_msg = verify_business_number(b_no)
    
    if is_valid:
        return Response({"message": f"사용 가능한 사업자입니다 ({status_msg})"}, status=200)
    else:
        return Response({"error": f"가입 불가: {status_msg}"}, status=400)

# 회원가입 api
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    data = request.data
    role = data.get('role')
    username = data.get('username')
    password = data.get('password')
    nickname = data.get('nickname')
    raw_b_no = data.get('business_number')
    b_no = raw_b_no.replace('-', '').strip() if raw_b_no else None

    if not username or not password:
        return Response({"error": "아이디와 비밀번호를 입력해주세요."}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "이미 사용중인 아이디입니다."}, status=400)

    try:
        if not nickname or str(nickname).strip() == "":
            suffix = f"{random.randint(1000, 9999)}"
            nickname = f"사장님{suffix}" if role == 'owner' else f"손님{suffix}"

        user = User.objects.create_user(
            username=username, 
            password=password, 
            is_owner=(role == 'owner'),
            nickname=nickname
        )

        if role == 'owner':
            if b_no:
                if User.objects.filter(business_number=b_no).exists():
                    user.delete()
                    return Response({"error": "이미 등록된 사업자 번호입니다."}, status=400)

                is_valid, msg = verify_business_number(b_no)
                if not is_valid:
                    user.delete()
                    return Response({"error": f"사업자 번호 검증에 실패했습니다: {msg}"}, status=400)

                user.business_number = b_no
            else:
                user.business_number = None

            user.store_name = data.get('store_name', '')
            user.store_address = data.get('store_address', '')
            user.save()

            Store.objects.create(
                owner=user,
                store_name=data.get('store_name', ''),
                store_address=data.get('store_address', ''),
                lat=data.get('lat'),
                lng=data.get('lng'),
            )
        else:
            user.business_number = None
            user.save()

        refresh = RefreshToken.for_user(user)
            
        return Response({
            "message": f"{nickname}님, 회원가입이 완료되었습니다!",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "nickname": user.nickname,
            "username": user.username,
            "role": 'owner' if user.is_owner else 'user'
        }, status=201)

    except Exception as e:
        if 'user' in locals() and user.pk:
            user.delete()
        print(f"회원가입 에러 발생: {str(e)}")
        return Response({"error": f"가입 중 오류 발생: {str(e)}"}, status=500)
