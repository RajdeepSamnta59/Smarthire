from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.views.generic import ListView
import random

# Create your views here.
def index(request):
    job_list = PostJob.objects.get_queryset().order_by('id')
    total_jobs = job_list.count()
    total_users = User.objects.all().count()
    total_companies = PostJob.objects.values('company_name').annotate(Count('company_name', distinct=True))
    query_num = 5
    paginator = Paginator(job_list, query_num)
    page = request.GET.get('page')
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)
    if qs.has_previous():
        page_show_min = (qs.previous_page_number() - 1) * query_num + 1
    elif total_jobs > 0:
        page_show_min = 1
    else:
        page_show_min = 0
    if qs.has_next():
        page_show_max = (qs.previous_page_number() + 1) * query_num - 1
    else:
        page_show_max = total_jobs
    context = {
        'query': qs,
        'job_listings': job_list,
        'job_len': total_jobs,
        'curr_page1': page_show_min,
        'curr_page2': page_show_max,
        'companies': total_companies.count(),
        'candidates': total_users
    }
    return render(request, "mysite/index.html", context=context)


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print("user: ", username)
        # print("password: ", password)
        user = auth.authenticate(username=username, password=password)
        # Debug: if user: print(user.is_active, user.is_staff)
        if user is not None:
            auth.login(request, user)
            # Debug: print(user)
            return redirect('index')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')

    else:
        return render(request, 'mysite/login.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        userType = request.POST['user_type']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        # phone = request.POST['phone']
        # address = request.POST['address']
        # linkedin_id = request.POST['linkedin_id']
        # github_id = request.POST['github_id']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken!')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken!')
                return redirect('register')
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                email=email, is_staff=userType, password=password1)
                user.save()
                # print("username: ", user)
                # print("password: ", password1)
                messages.info(request, 'User Created!')
                return redirect('login')
        else:
            messages.info(request, 'Password is not matching!')
            return redirect('register')
        # return redirect('index')

    else:
        return render(request, 'mysite/register.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


def about(request):
    return render(request, 'mysite/about.html')


@login_required(login_url='login')
def job_single(request, id):
    job_query = PostJob.objects.get(id=id)
    context = {
        'q': job_query,
    }
    return render(request, "mysite/job-single.html", context)


def job_listings(request):
    job_list = PostJob.objects.get_queryset().order_by('id')
    total_jobs = job_list.count()
    total_users = User.objects.all().count()
    total_companies = PostJob.objects.values('company_name').annotate(Count('company_name', distinct=True))
    query_num = 7
    paginator = Paginator(job_list, query_num)
    page = request.GET.get('page')
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)
    if qs.has_previous():
        page_show_min = (qs.previous_page_number() - 1) * query_num + 1
    elif total_jobs > 0:
        page_show_min = 1
    else:
        page_show_min = 0
    if qs.has_next():
        page_show_max = (qs.previous_page_number() + 1) * query_num - 1
    else:
        page_show_max = total_jobs
    context = {
        'query': qs,
        'job_listings': job_list,
        'job_len': total_jobs,
        'curr_page1': page_show_min,
        'curr_page2': page_show_max,
        'companies': total_companies.count,
        'candidates': total_users
    }
    return render(request, "mysite/job-listings.html", context=context)


@login_required(login_url='login')
def post_job(request):
    # Only recruiters can post jobs
    if not request.user.is_staff:
        messages.error(request, "Access denied. Only recruiters can post jobs.")
        return redirect('index')

    if request.method == "POST":
        title = request.POST['title']
        company_name = request.POST['company_name']
        employment_status = request.POST['employment_status']
        vacancy = request.POST['vacancy']
        gender = request.POST['gender']
        if 'details' in request.POST:
            details = request.POST['details']
        else:
            details = False
        # details = request.POST.get['details', False]
        if 'responsibilities' in request.POST:
            responsibilities = request.POST['responsibilities']
        else:
            responsibilities = ""
        # responsibilities = request.POST['responsibilities']
        experience = request.POST['experience']
        other_benefits = request.POST.get('other_benefits', "")
        job_location = request.POST['job_location']
        salary = request.POST['salary']
        application_deadline = request.POST.get('application_deadline', None)
        if application_deadline == "":
            application_deadline = None
        job = PostJob.objects.filter(title=title, company_name=company_name, employment_status=employment_status)
        print(job)
        if not job:
            ins = PostJob(title=title, company_name=company_name, employment_status=employment_status, vacancy=vacancy,
                          gender=gender, details=details,
                          responsibilities=responsibilities, experience=experience, other_benefits=other_benefits,
                          job_location=job_location, salary=salary, application_deadline=application_deadline,

                          required_skills=request.POST.get('required_skills', ''),
                          min_cgpa=float(request.POST.get('min_cgpa', 0.0) or 0.0),
                          min_experience=float(request.POST.get('min_experience', 0.0) or 0.0),
                          job_code=str(random.randint(100, 999)))
            ins.save()
            messages.info(request, 'Job successfully posted!')

            # storing job description
            # jobfilepath = 'jobDetails/'
            # job_desc = details + '\n' + responsibilities + '\n' + experience + '\n';
            # with open(jobfilepath + company_name + '_' + title + '.txt', 'w+') as file:
            #     file.write(re.sub(' +', ' ', job_desc))
            print("The data has been added into database!")
        else:
            messages.info(request, 'This job is already posted!')
            print('This job is already posted!')
        return redirect('job-listings')
    return render(request, 'mysite/post-job.html', {})


def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        # phone = request.POST['phone']
        if 'phone' in request.POST:
            phone = request.POST['phone']
        else:
            phone = False

        if 'subject' in request.POST:
            subject = request.POST['subject']
        else:
            subject = False

        if 'desc' in request.POST:
            desc = request.POST['desc']
        else:
            desc = False

        # desc = request.POST['desc']
        # print(name, email, phone, subject, desc)
        ins = Contact(name=name, email=email, phone=phone, subject=subject, desc=desc)
        ins.save()
        print("Data has been save in database!")
        return redirect('/')

    else:
        return render(request, "mysite/contact.html")


@login_required(login_url='login')
def applyjob(request, id):
    # Only applicants can apply for jobs
    if request.user.is_staff:
        messages.error(request, "Access denied. Recruiters cannot apply for jobs.")
        return redirect('index')

    job = PostJob.objects.get(id=id)
    print(job.id)
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        print(name, email)
        gender = request.POST['gender']
        experience = request.POST['experience']
        print(experience)

        coverletter = request.POST['coverletter']
        cv = request.FILES['cv']
        print(cv)
        print(cv)
        Apply_job.objects.filter(name=name, email__exact=email, company_name=job.company_name, title=job.title).delete()
        ins = Apply_job(name=name, email=email, cv=cv, experience=experience,coverletter=coverletter, company_name=job.company_name, gender=gender,
                            title=job.title)
        ins.save()
        messages.info(request, 'Successfully applied for the post!')
        print("The Data is saved into database!")
        return redirect('job-listings')

    return render(request, 'mysite/applyjob.html', {'company_name': job.company_name, 'title': job.title})


# @login_required
# def ranking(request, id):
#     job_query = PostJob.objects.get(id=id)
#     print(job_query.id, job_query.title, job_query.company_name)
#     jobfilename = job_query.company_name + '_' + job_query.title + '.txt'
#     job_desc = job_query.details + '\n' + job_query.responsibilities + '\n' + job_query.experience + '\n';
#     resumes_name = Apply_job.objects.filter(company_name=job_query.company_name, title=job_query.title,
#                                             cv__isnull=False)
#     resumes = [str(item.cv) for item in resumes_name]
#     resumes_new = [item.split(':')[0] for item in resumes]
#     resumes_new = [item for item in resumes_new if item != '']
#     result_arr = screen.res(jobfilename=jobfilename, job_desc=re.sub(r' +', ' ', job_desc.replace('\n', '').replace('\r', '')), list_of_resumes=resumes_new)
#     return render(request, 'mysite/ranking.html',
#                   {'items': result_arr, 'company_name': job_query.company_name, 'title': job_query.title})

@login_required(login_url='login')
def ranking(request, id):
    # Only recruiters can view rankings (is_staff=True for recruiters)
    if not request.user.is_staff:
        messages.error(request, "Access denied. Only recruiters can view candidate rankings.")
        return redirect('index')
    
    job_data = PostJob.objects.get(id=id)
    print(job_data.id, job_data.title, job_data.company_name)
    jobfilename = job_data.company_name + '_' + job_data.title + '.txt'
    job_desc = job_data.details + '\n' + job_data.responsibilities + '\n' + job_data.experience + '\n';
    resumes_data = Apply_job.objects.filter(company_name=job_data.company_name, title=job_data.title,
                                            cv__isnull=False)
    # Import heavy resume-processing module lazily to avoid import-time failures
    # when optional dependencies (like textract) are not installed.
    from mysite import screen
    result_arr = screen.res(resumes_data, job_data)
    return render(request, 'mysite/ranking.html',
                  {'items': result_arr, 'company_name': job_data.company_name, 'title': job_data.title, 'job_id': job_data.id})


class SearchView(ListView):
    model = PostJob
    template_name = 'mysite/search.html'
    context_object_name = 'all_job'

    def get_queryset(self):
        return self.model.objects.filter(title__contains=self.request.GET['title'],
                                         job_location__contains=self.request.GET['job_location'],
                                         employment_status__contains=self.request.GET['employment_status'])


@login_required(login_url='login')
def export_ranking_excel(request, id):
    # Only recruiters can export rankings (is_staff=True for recruiters)
    if not request.user.is_staff:
        messages.error(request, "Access denied. Only recruiters can export candidate rankings.")
        return redirect('index')
    
    job_data = PostJob.objects.get(id=id)
    resumes_data = Apply_job.objects.filter(company_name=job_data.company_name, title=job_data.title, cv__isnull=False)

    from mysite import screen
    # Reuse the ranking logic to get the sorted list
    result_arr = screen.res(resumes_data, job_data)
    
    import pandas as pd
    # Create DataFrame
    df = pd.DataFrame(result_arr)
    
    # Select and Rename columns for export
    columns_to_export = ['rank', 'name', 'email', 'score', 'skills_match', 'experience', 'cgpa', 'college', 'skills', 'cv_url']
    df_export = df[columns_to_export].copy()
    df_export.columns = ['Rank', 'Name', 'Email', 'Total Score', 'Skills Match %', 'Experience (Yrs)', 'CGPA', 'College', 'Extracted Skills', 'Resume Link']
    
    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Ranking_{job_data.company_name}_{job_data.title}.xlsx"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Ranked Candidates')
        
    return response


from mysite.resume_generator import generate_resume_content

def generate_resume(request):
    if request.method == 'POST':
        data = {
            'fullname': request.POST.get('fullname'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'summary': request.POST.get('summary'),
            'skills': request.POST.get('skills'),
            'experience': request.POST.get('experience'),
            'education': request.POST.get('education'),
        }
        
        resume_content = generate_resume_content(data)
        
        # Return as a downloadable HTML file (or PDF if we added a converter)
        response = HttpResponse(resume_content, content_type='text/html')
        # response['Content-Disposition'] = f'attachment; filename="{data["fullname"]}_Resume.html"'
        return response
        
    return render(request, 'mysite/generate_resume.html')

