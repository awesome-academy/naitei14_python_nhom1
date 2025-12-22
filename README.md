# naitei14_python_nhom1

## Social login (Google/Facebook)

Ứng dụng hỗ trợ đăng nhập bằng Google và Facebook thông qua `social-auth-app-django`.

### Cài đặt phụ thuộc
```
pip install social-auth-app-django
```

### Biến môi trường cần thêm vào `.env`
```
GOOGLE_OAUTH_CLIENT_ID=<your-google-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<your-google-client-secret>

FACEBOOK_APP_ID=<your-facebook-app-id>
FACEBOOK_APP_SECRET=<your-facebook-app-secret>
```

Sau khi cấu hình, chạy lại server và thử các nút đăng nhập Google/Facebook trên trang đăng nhập.