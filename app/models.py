from django.db import models
from django.utils import timezone
created_at = models.DateTimeField(auto_now_add=True, default=timezone.now)

class UserMaster(models.Model):
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)  # ✅ fixed
    otp = models.CharField(max_length=10, null=True, blank=True)
    role = models.CharField(max_length=50)      # ✅ fixed
    is_active = models.BooleanField(default=True)   # ✅ fixed
    is_verified = models.BooleanField(default=False)  # ✅ typo fixed
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ renamed for clarity
    updated_at = models.DateTimeField(auto_now=True)      # ✅ fixed to auto_now

class Candidate(models.Model):
    user_id = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    dob = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)  # ✅ fixed
    profile_pic = models.ImageField(upload_to="candidate/")
    resume = models.FileField(upload_to="candidate/", null=True, blank=True)
    job_role = models.CharField(max_length=100, blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    salary_expectation = models.CharField(max_length=50, blank=True, null=True)
    current_company = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)


class Company(models.Model):
    user_id = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100)
    company_email = models.EmailField()
    contact = models.CharField(max_length=15)
    address = models.CharField(max_length=150)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    company_logo = models.ImageField(upload_to='company/', null=True, blank=True)

    # ✅ Newly added fields
    company_description = models.TextField(null=True, blank=True)  # ✅ Remove default

    company_website = models.URLField(null=True, blank=True)
    linkedin_profile = models.URLField(null=True, blank=True)
    industry_type = models.CharField(max_length=100, null=True, blank=True)
    services_offered = models.TextField(null=True, blank=True)
    mission_statement = models.TextField(null=True, blank=True)
    team_size = models.CharField(max_length=50, null=True, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
    
#####################JobDetails############################################
class JobDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    job_title = models.CharField(max_length=100)
    job_description = models.TextField()
    qualifications = models.TextField()
    responsibilities = models.TextField()
    location = models.CharField(max_length=100)
    
    salary_package = models.CharField(max_length=50)
    experience_required = models.CharField(max_length=50)

    # Optional overrides (auto-filled from Company but editable)
    company_website = models.URLField(null=True, blank=True)
    company_email = models.EmailField()
    company_contact = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.company.company_name}"


##############################Apply Jobs#########################################
class ApplyJob(models.Model):
    STATUS_CHOICES = [
        ('Viewed', 'Viewed'),
        ('In Process', 'In Process'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    job = models.ForeignKey('JobDetails', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    experience = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resume/')
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Viewed')  # ✅ Added

    def __str__(self):
        return f"{self.name} applied for {self.job.job_title}"

    
class SavedJob(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    job = models.ForeignKey('JobDetails', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'job')  # ✅ Prevent duplicate saves

    def __str__(self):
        return f"{self.candidate.firstname} saved {self.job.job_title}"
