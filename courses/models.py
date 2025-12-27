from django.db import models
from django.contrib.auth.models import User

# ------------------------
# Course Model
# ------------------------
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # latest courses first

    def __str__(self):
        return self.title


# ------------------------
# Module Model
# ------------------------
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']  # optional: order by creation

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# ------------------------
# Lesson Model
# ------------------------
class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


# ------------------------
# Enrollment Model
# ------------------------
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)  # percentage

    class Meta:
        unique_together = ('user', 'course')  # prevent duplicate enrollments
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


# ------------------------
# Feedback Model
# ------------------------
class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ FIX

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"



# ------------------------
# Payment Model
# ------------------------
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.status})"
