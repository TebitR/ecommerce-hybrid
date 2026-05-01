from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CheckoutValidateSerializer, CheckoutCreateSerializer


class CheckoutValidateView(APIView):
    def post(self, request):
        serializer = CheckoutValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.validated_data["summary"], status=status.HTTP_200_OK)


class CheckoutCreateView(APIView):
    def post(self, request):
        serializer = CheckoutCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = serializer.save()
            return Response({
                "order_id": order.id,
                "order_number": order.order_number,
                "status": order.status,
                "subtotal": str(order.subtotal),
                "tax_amount": str(order.tax_amount),
                "total_amount": str(order.total_amount),
                "created_at": order.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
