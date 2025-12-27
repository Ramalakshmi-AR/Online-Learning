from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Module, Lesson, Enrollment, Feedback, Payment
from .forms import UserRegisterForm, FeedbackForm
from django.conf import settings
import razorpay

# Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def home(request):
    courses = Course.objects.all()
    return render(request, 'courses/home.html', {'courses': courses})


# Register
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration Successful!")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'courses/register.html', {'form': form})

# Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Credentials")
    return render(request, 'courses/login.html')

# Logout
def user_logout(request):
    logout(request)
    return redirect('home')

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    enrollments = request.user.enrollments.all()
    return render(request, 'courses/dashboard.html', {
        'enrollments': enrollments
    })

# Course Detail
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    modules = course.modules.all()
    return render(request, 'courses/course_detail.html', {'course': course, 'modules': modules, 'enrolled': enrolled})

# Enroll in Course
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, "Enrolled Successfully!")
    return redirect('course_detail', course_id=course.id)

@login_required
def add_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # prevent duplicate feedback
    feedback = Feedback.objects.filter(course=course, user=request.user).first()

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.course = course
            feedback.user = request.user
            feedback.save()
            messages.success(request, "✅ Feedback submitted successfully")
            return redirect('course_detail', course.id)
    else:
        form = FeedbackForm(instance=feedback)

    return render(request, 'courses/feedback.html', {
        'form': form,
        'course': course
    })

@login_required
def buy_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    order = client.order.create({
        "amount": int(course.price * 100),  # rupees → paise
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "course": course,
        "order": order,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    }

    return render(request, "courses/payment.html", context)


@login_required
def payment_success(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Auto-enroll user (safe from duplicates)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        messages.success(request, "🎉 Payment successful! You are now enrolled.")
    else:
        messages.info(request, "You are already enrolled in this course.")

    return redirect('dashboard')