from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _


# 헬퍼 클래스 - 유저를 생성할 때 사용
class UserManager(BaseUserManager):
    def create_user(self, user_name, email, password, **kwargs):
        """
        주어진 이름, 이메일, 비밀번호로 User 인스턴스 생성
        """
        if not user_name:
            raise ValueError('이름은 필수 항목입니다.')    
        if not email:
            raise ValueError('이메일은 필수 항목입니다.')
        if not password:
            raise ValueError('비밀번호는 필수 항목입니다.')
        
        user = self.model(
            user_name = user_name,
            email = email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, user_name=None, email=None, password=None, **extra_fields):
        """
        주어진 이름, 이메일, 비밀번호로 User 인스턴스 생성
        단, 최상위 사용자이므로 권한 부여
        """
        superuser = self.create_user(
            user_name = user_name,
            email = email,
            password = password,
        )
        
        superuser.is_active = True
        superuser.is_staff = True
        superuser.is_superuser = True
        
        superuser.save(using=self._db)
        return superuser
    
    
# AbstractBaseUser를 상속해서 유저 커스텀
class User(AbstractBaseUser, PermissionsMixin):
    # 입력 정보
    user_name = models.CharField(max_length=30, null=False, blank=False)
    email = models.CharField(max_length=30, unique=True, null=False, blank=False)
    
    # 자동 입력 정보 - (선택)
    date_joined = models.DateTimeField(_('created_at'), auto_now_add=True)
    
    # 권한 관련
    is_active = models.BooleanField(_('active_status'), default=True)
    is_staff = models.BooleanField(_('staff_status'), default=False)
    is_superuser = models.BooleanField(_('superuser_status'), default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']
    
    # 헬퍼 클래스 사용
    objects = UserManager()