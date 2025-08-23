from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Candidate, JobDetails, UserMaster ,Company,ApplyJob,SavedJob
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import check_password
from datetime import datetime
from .models import JobDetails
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
print("✅ views.py loaded successfully")
# app/views.py
from django.http import JsonResponse
from django.conf import settings
import google.generativeai as genai

import google.generativeai as genai
genai.configure(api_key="AIzaSyBhfwGIdouhpEQ-Bpmwa_FCAwxzP9Kc3SM")

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Introduce yourself in 2 lines")
print(response.text)


genai.configure(api_key=settings.GOOGLE_API_KEY)

def chatbot(request):
    message = request.GET.get("message", "")
    if not message:
        return JsonResponse({"reply": "⚠️ Please type something."})

    try:
        # Using Gemini Flash 2.0
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(message)

        reply_text = response.text if response and response.text else "⚠️ Sorry, I didn’t understand."
        return JsonResponse({"reply": reply_text})

    except Exception as e:
        return JsonResponse({"reply": f"⚠️ Error: {str(e)}"})






def Index_Page(request):
    print("views.py loaded!")

    return render(request, 'app/index.html')

def job_listing(request):
    return render(request, 'app/job_listing.html')

def about(request):
    return render(request, 'app/about.html')

def contact(request):
    return render(request,'app/contact.html')

def candidate_register(request):
    if request.method == "POST":
        email = request.POST['email']
        
        # Check if email already exists
        if UserMaster.objects.filter(email=email).exists():
            messages.warning(request, " ⚠️ User already registered. Please login.")
            return redirect('candidate_register')

        # Proceed with registration
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        contact = request.POST['contact']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        dob = request.POST['dob']
        gender = request.POST['gender']
        profile_pic = request.FILES.get('profile_pic')

        # Create UserMaster entry
        user = UserMaster.objects.create(
            email=email,
            password=request.POST['password'],
            role='Candidate'
        )

        # Create Candidate entry
        Candidate.objects.create(
            user_id=user,
            firstname=firstname,
            lastname=lastname,
            contact=contact,
            state=state,
            city=city,
            address=address,
            dob=dob,
            gender=gender,
            profile_pic=profile_pic
        )

        messages.success(request, "✅ Candidate registered successfully!")
        return redirect('candidate_register')

    return render(request, 'app/candidate_register.html')

def candidate_login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # Check if user with this email and password exists
        try:
            user = UserMaster.objects.get(email=email, password=password)
            if user.role == "Candidate":
                request.session['email'] = user.email
                request.session['id'] = user.id

                
                return redirect('candidate_dashboard')  # Replace with actual dashboard url
            else:
                messages.error(request, "You are not authorized as Candidate.")
                return redirect('candidate_login')
        except UserMaster.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('candidate_login')

    return render(request, 'app/candidate_login.html')


def candidate_dashboard(request):
    if 'email' not in request.session:
        # User is not logged in, redirect to login page
        return redirect('candidate_login')

    user = UserMaster.objects.get(email=request.session['email'])
    candidate = Candidate.objects.get(user_id=user)
    return render(request, 'app/candidate/candidate_dashboard.html', {'candidate': candidate})

#-------------------Candidate-Update-Profile---------------------------
def candidate_update_profile(request):
    if 'email' not in request.session:
        messages.error(request, "Please log in to update your profile.")
        return redirect('candidate_login')

    user = UserMaster.objects.get(email=request.session['email'])  # ✅ Get the logged-in user
    candidate = Candidate.objects.get(user_id=user)  # ✅ Get candidate using the user

    if request.method == "POST":
        candidate.firstname = request.POST.get('firstname')
        candidate.lastname = request.POST.get('lastname')
        candidate.contact = request.POST.get('contact')
        candidate.state = request.POST.get('state')
        candidate.city = request.POST.get('city')
        candidate.address = request.POST.get('address')
        candidate.dob = request.POST.get('dob')
        candidate.gender = request.POST.get('gender')

        # ✅ Newly added fields
        candidate.job_role = request.POST.get('job_role')
        # Handle number fields safely
        experience = request.POST.get('experience')
        candidate.experience = int(experience) if experience else None

        salary = request.POST.get('salary_expectation')
        candidate.salary_expectation = int(salary) if salary else None
        candidate.github = request.POST.get('github')
        candidate.linkedin = request.POST.get('linkedin')
        candidate.portfolio = request.POST.get('portfolio')
        candidate.skills = request.POST.get('skills')
        candidate.bio = request.POST.get('bio')
        candidate.current_company = request.POST.get('current_company')

        if 'profile_pic' in request.FILES:
            candidate.profile_pic = request.FILES['profile_pic']

        if 'resume' in request.FILES:
            candidate.resume = request.FILES['resume']

        candidate.save()
        messages.success(request, "✅ Profile updated successfully!")
        return redirect('candidate_update_profile')

    return render(request, 'app/candidate/update_profile.html', {'candidate': candidate})


def candidate_job_list(request):
    if 'email' not in request.session:
        messages.error(request, "Please log in to view job listings.")
        return redirect('candidate_login')

    jobs = JobDetails.objects.select_related('company').order_by('-created_at')
    return render(request, "app/candidate/job_list_apply.html", {"jobs": jobs})



def candidate_job_details(request, job_id):
    job = get_object_or_404(JobDetails, id=job_id)
    return render(request, "app/candidate/job_details_partial.html", {"job": job})

#################--------Apply Job Ajax---------######################################
def apply_job_ajax(request, job_id):
    if request.method == "GET":
        job = get_object_or_404(JobDetails, id=job_id)

        # Get logged-in user's candidate profile
        if 'email' not in request.session:
            return JsonResponse({"success": False, "message": "You must be logged in as a candidate."}, status=403)
            
        user = get_object_or_404(UserMaster, email=request.session['email'])
        candidate = Candidate.objects.get(user_id=user)  # ✅ Get candidate using the user
        print(candidate)
        print(candidate.resume)
        return render(request, "app/candidate/apply_form.html", {
            "job": job,
            "candidate": candidate,'user':user
        })  

    elif request.method == "POST":
        if 'email' not in request.session:
            return JsonResponse({"success": False, "message": "You must be logged in as a candidate."}, status=403)

        user = get_object_or_404(UserMaster, email=request.session['email'])
        candidate = get_object_or_404(Candidate, user_id=user)

        job = get_object_or_404(JobDetails, id=request.POST.get("job_id"))
        company = job.company

        resume = request.FILES.get("resume") or candidate.resume

        # Create ApplyJob record
        ApplyJob.objects.create(
            candidate=candidate,
            company=company,
            job=job,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            experience=request.POST.get("experience"),
            resume=resume,
            cover_letter=request.POST.get("cover_letter")
        )

        return JsonResponse({"success": True, "message": "Application submitted successfully!"})
    
# views.py
from django.http import JsonResponse
from .models import JobDetails, Candidate, SavedJob, UserMaster

def save_job(request, job_id):
    if request.method == "POST":
        if 'email' not in request.session:
            return JsonResponse({"success": False, "error": "You must be logged in as a candidate."}, status=403)

        try:
            job = JobDetails.objects.get(id=job_id)
            user = UserMaster.objects.get(email=request.session['email'])
            candidate = Candidate.objects.get(user_id=user)

            # Save job
            saved, created = SavedJob.objects.get_or_create(candidate=candidate, job=job)

            if created:
                return JsonResponse({"success": True, "message": "Job saved successfully!"})
            else:
                return JsonResponse({"success": False, "error": "Job already saved."})

        except JobDetails.DoesNotExist:
            return JsonResponse({"success": False, "error": "Job not found"})
        except Candidate.DoesNotExist:
            return JsonResponse({"success": False, "error": "Candidate not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})

#######################Saved Jobs List##################################3
# views.py
def saved_jobs_list(request):
    if 'email' not in request.session:
        messages.error(request, "Please log in to view saved jobs.")
        return redirect('candidate_login')

    try:
        user = UserMaster.objects.get(email=request.session['email'])
        candidate = Candidate.objects.get(user_id=user)

        saved_jobs = SavedJob.objects.filter(candidate=candidate).select_related("job")
    except (UserMaster.DoesNotExist, Candidate.DoesNotExist):
        saved_jobs = []

    return render(request, "app/candidate/saved_jobs_list.html", {"saved_jobs": saved_jobs})


###############Candidate Logout#################################
def candidate_logout(request):
    logout(request)  # Clears the session and logs out the user
    return redirect('candidate_login')  # Redirect to your login page (use your login URL name)


#---------------------Company Register-----------------------------

def company_register(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        contact = request.POST.get("contact")
        company_name = request.POST.get("company_name")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address = request.POST.get("address")
        company_logo = request.FILES.get("company_logo")  # ✅

        # ✅ Fix: Check in UserMaster, not Company
        if UserMaster.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("company_register")

        user = UserMaster.objects.create(
            email=email,
            password=password,
            role="Company",
        )

        Company.objects.create(
            user_id=user,
            firstname=firstname,
            lastname=lastname,
            contact=contact,
            company_name=company_name,
            company_email=email,
            state=state,
            city=city,
            address=address,
            company_logo=company_logo  # ✅
        )

        messages.success(request, "Company registered successfully!")
        return redirect("company_register")

    return render(request, "app/company_register.html")

# views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Company

def company_login(request):
    if request.method == 'POST':
        email = request.POST['email'].strip()
        password = request.POST['password'].strip()

        try:
            # Get the UserMaster record first
            user = UserMaster.objects.get(email=email, password=password, role='Company')

            # Now get the associated Company record
            company = Company.objects.get(user_id=user)

            # Save session
            request.session['company_id'] = company.id
            request.session['role'] = user.role
            request.session['email'] = user.email

            messages.success(request, 'Login Successful!')
            return redirect('company_dashboard')

        except UserMaster.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('company_login')

        except Company.DoesNotExist:
            messages.error(request, 'No company found for this user.')
            return redirect('company_login')

    return render(request, 'app/company_login.html')


def company_dashboard(request):
    try:
        company_id = request.session.get('company_id')
        company = Company.objects.get(id=company_id)
        print(company)
        return render(request, 'app/company/company_dashboard.html', {'company': company})
    except Company.DoesNotExist:
        messages.error(request, 'Company not found. Please log in again.')
        return redirect('company_login')


#--------------------------Company Profile-----------------------------------
def company_profile(request):
    try:
        company_id = request.session.get('company_id')
        company = Company.objects.get(id=company_id)

        if request.method == 'POST':
            company.firstname = request.POST.get('firstname') or company.firstname
            company.lastname = request.POST.get('lastname') or company.lastname
            company.company_name = request.POST.get('company_name') or company.company_name
            company.company_email = request.POST.get('company_email') or company.company_email
            company.contact = request.POST.get('contact') or company.contact
            company.address = request.POST.get('address') or company.address
            company.state = request.POST.get('state') or company.state
            company.city = request.POST.get('city') or company.city
            company.company_description = request.POST.get('company_description') or company.company_description
            company.company_website = request.POST.get('company_website') or company.company_website
            company.linkedin_profile = request.POST.get('linkedin_profile') or company.linkedin_profile
            company.industry_type = request.POST.get('industry_type') or company.industry_type
            company.services_offered = request.POST.get('services_offered') or company.services_offered
            company.mission_statement = request.POST.get('mission_statement') or company.mission_statement
            company.team_size = request.POST.get('team_size') or company.team_size

            # Optional: Handle founded_year safely
            founded_year = request.POST.get('founded_year')
            if founded_year:
                try:
                    company.founded_year = int(founded_year)
                except ValueError:
                    messages.warning(request, "Founded year must be a valid number.")

            # Optional: Handle file upload for company logo
            if 'company_logo' in request.FILES:
                company.company_logo = request.FILES['company_logo']

            company.updated_at = datetime.now()
            company.save()

            messages.success(request, "Company profile updated successfully.")
            return redirect('company_profile')  # Reload the page after update

        return render(request, 'app/company/company_profile.html', {'company': company})

    except Company.DoesNotExist:
        messages.error(request, 'Company not found. Please log in again.')
        return redirect('company_login')
    
#########---------------------Post Job --------------#########################
def post_job(request):
    try:
        company_id = request.session.get('company_id')
        if not company_id:
            messages.error(request, 'You must be logged in to post a job.')
            return redirect('company_login')

        company = Company.objects.get(id=company_id)

        if request.method == "POST":
            job = JobDetails(
                job_title=request.POST['job_name'],
                company=company,  # ✅ Pass the object, not the name
                job_description=request.POST['job_description'],
                qualifications=request.POST['qualification'],
                responsibilities=request.POST['responsibilities'],
                location=request.POST['location'],
                experience_required=request.POST['experience'],
                salary_package=request.POST['salary_package'],
                company_contact=company.contact,
                company_email=company.company_email,
                company_website=company.company_website,
            )
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('post_job')

        # GET request
        return render(request, "app/company/post_job.html", {'company': company})

    except Company.DoesNotExist:
        messages.error(request, 'Company not found. Please log in again.')
        return redirect('company_login')

#------------Job Listing-------------------
def job_listings(request):
    company_id = request.session.get('company_id')
    if not company_id:
        messages.error(request, "Please log in first.")
        return redirect('company_login')

    jobs = JobDetails.objects.filter(company_id=company_id).order_by('-created_at')
    return render(request, "app/company/company_job_list.html", {"jobs": jobs})

####################################View Applications####################################################
def view_applications(request):
    """
    Show all job applications for jobs posted by the logged-in company.
    """
    company_id = request.session.get('company_id')
    if not company_id:
        messages.error(request, "Please log in first.")
        return redirect('company_login')

    # Get the company object
    company = Company.objects.get(id=company_id)

    # Get all applications for jobs posted by this company
    applications = (
        ApplyJob.objects
        .select_related('candidate', 'job')
        .filter(job__company=company)
        .order_by('-applied_at')
    )

    return render(request, 'app/company/company_applications.html', {
        'applications': applications
    })


from django.shortcuts import get_object_or_404

from django.http import JsonResponse

def application_details(request, app_id):
    try:
        application = get_object_or_404(ApplyJob, id=app_id)
        return render(request, 'app/company/application_details_partial.html', {'app': application})
    except Exception as e:
        import traceback
        print("ERROR in application_details:", traceback.format_exc())  # Logs full error in console
        return JsonResponse({'error': str(e)}, status=500)

############################ADMIN MODULE#######################################
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Hardcoded admin credentials
        if username == "admin@gmail.com" and password == "admin":
           
            return redirect("admin_dashboard")  # redirect to admin dashboard page
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "app/admin_login.html")

def admin_dashboard(request):
    return render(request,"app/admin_dashboard.html")

def Adminuserlist(request):
    # Fetch all Candidate records with related UserMaster in one query
    all_user = Candidate.objects.select_related('user_id').all()
    return render(request, "app/admin/userlist.html", {'all_user': all_user})

def Admincompanylist(request):
    all_company =UserMaster.objects.filter(role="company")
    return render(request,'app/admin/companylist.html',{'all_company':all_company})

def delete_user(request, user_id):
    user = get_object_or_404(UserMaster, id=user_id)
    user.delete()  # Will cascade delete all related Candidate/Company data
    return redirect('admin_user_list')  # Replace with your admin list URL name

def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.delete()
    messages.success(request, "✅ Company deleted successfully.")
    return redirect('company_list')

def toggle_company_verification(request, user_id):
    user = get_object_or_404(UserMaster, id=user_id, role="company")
    user.is_verified = not user.is_verified
    user.save()
    if user.is_verified:
        messages.success(request, f"✅ {user.email} has been verified.")
    else:
        messages.warning(request, f"⚠️ {user.email} has been marked as Not Verified.")
    return redirect('company_list')

def admin_logout(request):
    logout(request)  # Clears the session and logs out the user
    return redirect('admin_login')  # Redirect to your login page (use your login URL name)