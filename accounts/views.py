from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import verify_business_number

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    data = request.data
    role = data.get('role')  
    username = data.get('username')
    password = data.get('password')
    b_no = data.get('business_number', '').replace('-', '')  #사업자번호에 - 제거

    if not username or not password:
        return Response({"error": "아이디와 비밀번호를 입력해주세요."}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "이미 사용중인 아이디입니다."}, status=400)
    
    try:
        if role == 'owner':
            if not b_no or len(b_no) != 10:
                return Response({"error": "사업자 번호를 다시 확인해주세요."}, status=400)
            if not verify_business_number(b_no):
                return Response({"error": "유효하지 않은 사업자 번호입니다."}, status=400)
            if User.objects.filter(business_number=b_no).exists():
                return Response({"error": "이미 등록된 사업자 번호입니다."}, status=400)

        user = User.objects.create_user(    # 손님으로 등록시 기본 생성 항목
            username=username,
            password=password,
            is_owner=(role == 'owner'),
            # phone_number=data.get('phone_number', '')
        )
        
        if role == 'owner':     # 사장님으로 등록시 기본 생성 항목
            user.business_number = b_no
            user.store_name = data.get('store_name')
            user.store_address = data.get('store_address')
            user.save()
        else:
            user.nickname = data.get('nickname', username)      #닉네임 공란일면 임의로 생성
            user.save()

        refresh = RefreshToken.for_user(user)
            
        return Response({
            "message": f"{username}님, 회원가입이 완료되었습니다!",
            "access": str(refresh.access_token),
            "nickname": user.nickname if not user.is_owner else user.username,
            "role": 'owner' if user.is_owner else 'user'
        }, status=201)

    except Exception as e:
        return Response({"error": f"가입 중 오류 발생: {str(e)}"}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_biz(request):
    b_no = request.data.get('business_number', '').replace('-', '').strip()
    
    if not b_no or len(b_no) != 10:
        return Response({"error": "10자리 사업자 번호를 입력해주세요."}, status=400)
    
    is_valid, status_msg = verify_business_number(b_no)
    
    if is_valid:
        return Response({"message": f"사용 가능한 사업자입니다 ({status_msg})"}, status=200)
    else:
        return Response({"error": f"가입 불가: {status_msg}"}, status=400)