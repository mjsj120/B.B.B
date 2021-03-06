from django.shortcuts import render, redirect, get_object_or_404
from .models import ReadingRecord
from django.utils import timezone
from .form import RecordForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

# Create your views here.

def record_list(request):
    records = ReadingRecord.objects.all()[::-1]
    paginator = Paginator(records, 10)
    page= request.GET.get('page')
    if page == "" or page == None:
        page = 1
    records_page = paginator.get_page(page)
    start = max(int(page)-5, 1)
    end = min(int(page)+5, paginator.num_pages)
    return render(request, 'record_list.html', {'records':records, 'records_page' : records_page, 'range' : [i for i in range(start, end+1)]})

# def recoed_request(request, username):

@login_required(login_url='/account/login/')
def new(request):
    if request.method == "POST":
        form = RecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit = False)
            record.publisher = request.user
            record.save()
            messages.success(request,'새 독서 기록이 등록되었습니다.')
            return redirect('record_list')
    form = RecordForm()
    return render(request, 'new.html', {'form':form})

def detail(request, record_id):
    record = get_object_or_404(ReadingRecord, pk = record_id)
    return render(request, 'detail.html', {'record':record})


@login_required(login_url='/account/login/')
def edit(request, record_id):
    user = request.user
    if user.is_authenticated and ReadingRecord.objects.get(pk=record_id).publisher == user:
        form = RecordForm(instance = ReadingRecord.objects.get(pk = record_id))
        
        messages.success(request,'독서 기록이 수정되었습니다.')
        return render(request, 'edit.html', {'form':form, 'record_id':record_id})
    elif user.is_authenticated:
        messages.error(request, "본인의 글만 수정할 수 있습니다.")
        return detail(request, record_id)
    else:
        messages.error(request, "로그인 후, 글을 수정할 수 있습니다.")
        return redirect("login")

@login_required(login_url='/account/login/')
def update(request, record_id):
    update_record = get_object_or_404(ReadingRecord, pk = record_id)
    update_record.title = request.POST['title']
    
    try:
        update_record.rep_img = request.FILES['rep_img']
    except:
        pass
    update_record.author = request.POST['author']
    update_record.record_title = request.POST['record_title']
    update_record.read_at = request.POST['read_at']
    update_record.category = request.POST['category']
    update_record.record_body = request.POST['record_body']
    update_record.save()
    return redirect('record_detail', update_record.id)

def delete(request, record_id):
    user = request.user
    where = ""
    try:
        where = request.GET.get('where')
    except:
        pass
    if user.is_authenticated and ReadingRecord.objects.get(pk=record_id).publisher == user:
        delete_record = get_object_or_404(ReadingRecord, pk = record_id)
        delete_record.delete()
        messages.success(request,"독서 기록이 삭제되었습니다.")
        if where == 'user_page':
            return redirect("user")
        else:
            return redirect('record_list')
    elif user.is_authenticated:
        messages.error(request,"본인의 글만 삭제할 수 있습니다.")
        return detail(request, record_id)
    else:
        messages.error(request, "로그인 후, 글을 수정할 수 있습니다.")
        return redirect("login")