from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from shealth.forms import DoctorCreationForm, PatientCreationForm
from shealth.models import Doctor, Patient, Appointment, User, Record
from shealth.serializers import RecordSerializer, UserSerializer
from shealth.qrcodeGenerate import *
from wsgiref.util import FileWrapper
from django.http import HttpResponse
import os


class DoctorRegisterView(APIView):
    def post(self, request):
        form = DoctorCreationForm(request.data)
        if form.is_valid():
            form.save()
            return Response({"detail": "Doctor registered successfully"})
        else:
            return Response(
                {"detail": "Doctor registration failed", "errors": form.errors}
            )


class PatientRegisterView(APIView):
    def post(self, request):
        form = PatientCreationForm(request.data)
        if form.is_valid():
            form.save()
            return Response({"detail": "Patient registered successfully"})
        else:
            return Response(
                {"detail": "Patient registration failed", "errors": form.errors}
            )


class DoctorQRCode(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # get doctor id
        doctor_id = Doctor.objects.get(user=request.user).doc_id
        print(doctor_id)
        qrcode = createQR(doctor_id)
        qr = open(qrcode, "rb")
        response = HttpResponse(FileWrapper(qr), content_type="image/png")

        # Remove qr code from the server
        os.system(f"rm {qrcode}")

        return response


class UploadDocs(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser, FormParser, MultiPartParser)

    def post(self, request, format=None):
        data = request.data
        print(data)
        data.update({"patient": self.request.user.uuid})
        print(data)
        serializer = RecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "File uploaded successfully"})
        else:
            return Response(
                {"detail": "File upload failed", "errors": serializer.errors}
            )


class UserDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class DoctorDocIdView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        doctor_id = Doctor.objects.get(user=request.user).doc_id
        print(doctor_id)
        return Response({"doc_id": doctor_id})


class GiveAccessPatient(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        doc_id = request.data["doc_id"]
        print(doc_id)
        patient = request.user.patient
        doctor = None
        try:
            doctor = Doctor.objects.get(doc_id=doc_id)
        except:
            return Response({"detail": "Doctor not found"}, status=404)

        # check if the doctor and patient are already connected
        Appointment.objects.get_or_create(
            doctor=Doctor.objects.get(doc_id=doc_id), patient=patient
        )
        return Response({"message": "Access given to {}".format(doctor.user.email)})


def has_object_permission(self, request, email):
    if request.user.email == email:
        return True
    elif Appointment.objects.filter(
        doctor__user__email=request.user.email, patient__user__email=email
    ).exists():
        return True
    else:
        return False


class ListRecords(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        email = request.data["email"]
        if not has_object_permission(self, request, email):
            return Response(
                {"detail": "You do not have access to this patient"}, status=404
            )
        records = Record.objects.filter(patient__user__email=email)
        serializer = RecordSerializer(records, many=True)
        return Response(serializer.data)


class Index(APIView):
    def get(self, request):
        return Response({"detail": "Welcome to Shealth"})
