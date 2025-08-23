# app/context_processors.py
from .models import Company

def company_profile(request):
    company_data = None
    company_id = request.session.get('company_id')
    
    if company_id:
        try:
            company_data = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            company_data = None
    
    return {
        'company': company_data
}

from .models import UserMaster, Candidate

def candidate_profile(request):
    if 'email' in request.session:
        try:
            user = UserMaster.objects.get(email=request.session['email'])
            candidate = Candidate.objects.get(user_id=user)
            return {"candidate": candidate}  # ✅ Available on all templates
        except:
            return {}
    return {}

    
