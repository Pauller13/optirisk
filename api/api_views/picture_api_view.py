from rest_framework.views import APIView
from base.services.status_service import StatusService
from api.serializers import PictureUserSerializer
from user.models.custom_user_model import CustomUserModel
from cloudinary import uploader, api
from cloudinary.exceptions import NotFound

status_service = StatusService()
class PictureAPIView(APIView):
    
    def get(self, request):
        serializer = PictureUserSerializer(request.user)
        return status_service.status200(data=serializer.data)
    
    def post(self, request):
        user = CustomUserModel.objects.get(email=request.user.email)
        if user.picture:
            uploader.destroy(user.picture.name)
        serializer = PictureUserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return status_service.status200(data=serializer.data)
        return status_service.status400(data=serializer.errors)
    

def check_image_exists(image_name):
    print(api.resource(image_name))
    try:
        api.resource(image_name) # Permet de récupérer les infos de l'image
        return True
    except NotFound:
        return False