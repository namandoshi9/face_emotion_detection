from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from deepface import DeepFace
from django.db.models import Avg
from django.db.models.functions import TruncMonth
from calendar import month_abbr
from django.http import JsonResponse
from .forms import UserRegistrationForm
import cv2
import numpy as np
import base64
from .models import EmotionDetection
from django.http import StreamingHttpResponse
import csv
from django.http import HttpResponse

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)  # This is where the user variable is defined
            if user is not None:
                if user.is_active:
                    if user.is_staff and user.is_superuser:
                        login(request, user)
                        return redirect('emotion-view')
                    else:
                        login(request, user)
                        return redirect('emotion-view')
                else:
                    messages.error(request, "Your account is inactive.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login') 

def admin_dashboard_view(request):
    return render(request,'admin_dashboard.html')

def moderator_dashboard_view(request):
    return render(request,'moderator.html')

def profile_view(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})

def check_emotion_view(request):
    return render(request,'check_emotion.html')

def emotion_detection_view(request):
    return render(request, 'emotion_detection.html')



face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def analyze_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2RGB)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) == 0:
        return []

    emotions = []

    for (x, y, w, h) in faces:
        face_roi = rgb_image[y:y + h, x:x + w]
        result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
        emotions.append(result)
    
    return emotions

def capture_and_analyze(request):
    if request.method == 'POST':
        image_data = request.POST.get('image_data')
        nparr = np.fromstring(base64.b64decode(image_data.split(',')[1]), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        emotions = analyze_image(img)

        emotion_results = []

        # Get the logged-in user
        user = request.user

        for emotion_data in emotions:
            if emotion_data:
                emotion_values = emotion_data[0]['emotion']
                emotion_results.append(emotion_values)

                # Create EmotionDetection instance with user ID
                emotion_detection = EmotionDetection.objects.create(
                    user=user,  # Associate the EmotionDetection with the logged-in user
                    happy=emotion_values.get('happy', 0),
                    anger=emotion_values.get('angry', 0),
                    surprise=emotion_values.get('surprise', 0),
                    neutral=emotion_values.get('neutral', 0),
                    fear=emotion_values.get('fear', 0),
                    sad=emotion_values.get('sad', 0)
                )

                emotion_detection.save()

        return JsonResponse({'emotions': emotion_results})

    return JsonResponse({'error': 'Invalid request method'})



def view_emotions(request):
    return render (request,'check_graph.html')


from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

@login_required
def emotion_data_view(request):
    # Check if the user is an admin
    if request.user.is_superuser:
        # Admin user, fetch all emotion data
        emotion_data = EmotionDetection.objects.annotate(month=TruncMonth('date')).values('month').annotate(
            happy=Avg('happy'),
            anger=Avg('anger'),
            surprise=Avg('surprise'),
            neutral=Avg('neutral'),
            fear=Avg('fear'),
            sad=Avg('sad')
        ).order_by('month')
    else:
        # Non-admin user, fetch emotion data for the current user only
        emotion_data = EmotionDetection.objects.filter(user=request.user).annotate(month=TruncMonth('date')).values('month').annotate(
            happy=Avg('happy'),
            anger=Avg('anger'),
            surprise=Avg('surprise'),
            neutral=Avg('neutral'),
            fear=Avg('fear'),
            sad=Avg('sad')
        ).order_by('month')

    labels = [month_abbr[data['month'].month] for data in emotion_data]
    datasets = [
        {
            'label': 'Happy',
            'data': [data['happy'] for data in emotion_data],
            'backgroundColor': 'orange'
        },
        {
            'label': 'Anger',
            'data': [data['anger'] for data in emotion_data],
            'backgroundColor': 'red'
        },
        {
            'label': 'Surprise',
            'data': [data['surprise'] for data in emotion_data],
            'backgroundColor': 'yellow'
        },
        {
            'label': 'Neutral',
            'data': [data['neutral'] for data in emotion_data],
            'backgroundColor': 'green'
        },
        {
            'label': 'Fear',
            'data': [data['fear'] for data in emotion_data],
            'backgroundColor': 'purple'
        },
        {
            'label': 'Sad',
            'data': [data['sad'] for data in emotion_data],
            'backgroundColor': 'blue'
        }
    ]

    chart_data = {
        'labels': labels,
        'datasets': datasets
    }

    return render(request, 'check_graph.html', {'chart_data': chart_data})


def calender_view(request):
    return render(request,'calender.html')



def detect_emotions(request):
    # Load face cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Function to generate video stream
    def video_stream():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                face_roi = rgb_frame[y:y + h, x:x + w]
                result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                emotion = result[0]['dominant_emotion']
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                
                
                user = request.user  
                EmotionDetection.objects.create(
                    user=user,
                    happy=result[0]['emotion']['happy'],
                    anger=result[0]['emotion']['angry'],
                    surprise=result[0]['emotion']['surprise'],
                    neutral=result[0]['emotion']['neutral'],
                    fear=result[0]['emotion']['fear'],
                    sad=result[0]['emotion']['sad']
                )

            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')




@login_required
def export_emotion_data(request):
    # Check if the user is an admin
    if request.user.is_superuser:
        # Admin user, fetch all emotion data
        emotion_data = EmotionDetection.objects.all()
    else:
        # Non-admin user, fetch emotion data for the current user only
        emotion_data = EmotionDetection.objects.filter(user=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="emotion_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Happy', 'Anger', 'Surprise', 'Neutral', 'Fear', 'Sad'])

    for data in emotion_data:
        writer.writerow([data.date.strftime('%Y-%m-%d %H:%M:%S'), data.happy, data.anger, data.surprise, data.neutral, data.fear, data.sad])

    return response
