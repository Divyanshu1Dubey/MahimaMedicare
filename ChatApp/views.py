from multiprocessing import context
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Max, Subquery, OuterRef
from doctor.views import appointments
from .models import chatMessages
from django.contrib.auth import get_user_model
from  hospital.models import User as UserModel
from hospital.models import Patient
from doctor.models import Doctor_Information  , Appointment  
from django.db.models import Q
import json,datetime
from django.core import serializers
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

from django.db.models import Count, Q, Max, Subquery, OuterRef

@csrf_exempt
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request, pk):
    if request.user.is_patient:
        User = get_user_model()
        users = User.objects.all()
        patients = Patient.objects.get(user_id=pk)
        appointments = Appointment.objects.filter(patient=patients).filter(appointment_status='confirmed')
        doctor = Doctor_Information.objects.filter(appointment__in=appointments)

        # 🔹 Get unread counts (messages sent to this user but not yet read)
        unread_counts = chatMessages.objects.filter(
            user_to=request.user,
            is_read=False
        ).values('user_from').annotate(total=Count('id'))
        unread_map = {u['user_from']: u['total'] for u in unread_counts}

        chats = {}
        if request.method == 'GET' and 'u' in request.GET:
            chats = chatMessages.objects.filter(
                Q(user_from=request.user.id, user_to=request.GET['u']) |
                Q(user_from=request.GET['u'], user_to=request.user.id)
            ).order_by('date_created')

            # 👉 Mark as read kapag binuksan ni patient yung convo
            chatMessages.objects.filter(
                user_from=request.GET['u'],   # galing kay doctor
                user_to=request.user,         # papunta sa patient
                is_read=False
            ).update(is_read=True)

            doc = Doctor_Information.objects.get(user_id=request.GET['u'])

            context = {
                "page": "home",
                "users": users,
                "chats": chats,
                "patient": patients,
                "doctor": doctor,
                "doc": doc,
                "app": appointments,
                "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0),
                "unread_map": unread_map
            }
        elif request.method == 'GET' and 'search' in request.GET:
            query = request.GET.get('search')
            doctor = Doctor_Information.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )
            context = {
                "page": "home",
                "users": users,
                "patient": patients,
                "doctor": doctor,
                "unread_map": unread_map
            }
        else:
            context = {
                "page": "home",
                "users": users,
                "chats": chats,
                "patient": patients,
                "doctor": doctor,
                "app": appointments,
                "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0),
                "unread_map": unread_map
            }
        print(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
        return render(request, "chat.html", context)

    elif request.user.is_doctor:
        User = get_user_model()
        users = User.objects.all()
        doctor = Doctor_Information.objects.get(user_id=pk)
        appointments = Appointment.objects.filter(doctor=doctor).filter(appointment_status='confirmed')
        patients = Patient.objects.filter(appointment__in=appointments)

        # 🔹 Get unread counts for doctor
        unread_counts = chatMessages.objects.filter(
            user_to=request.user,
            is_read=False
        ).values('user_from').annotate(total=Count('id'))
        unread_map = {u['user_from']: u['total'] for u in unread_counts}

        chats = {}
        if request.method == 'GET' and 'u' in request.GET:
            chats = chatMessages.objects.filter(
                Q(user_from=request.user.id, user_to=request.GET['u']) |
                Q(user_from=request.GET['u'], user_to=request.user.id)
            ).order_by('date_created')

            # 👉 Mark as read kapag binuksan ni doctor yung convo
            chatMessages.objects.filter(
                user_from=request.GET['u'],   # galing kay patient
                user_to=request.user,         # papunta kay doctor
                is_read=False
            ).update(is_read=True)

            pat = Patient.objects.get(user_id=request.GET['u'])

            context = {
                "page": "home",
                "users": users,
                "chats": chats,
                "patient": patients,
                "doctor": doctor,
                "pat": pat,
                "app": appointments,
                "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0),
                "unread_map": unread_map
            }
        elif request.method == 'GET' and 'search' in request.GET:
            query = request.GET.get('search')
            patients = Patient.objects.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )
            context = {
                "page": "home",
                "users": users,
                "patient": patients,
                "app": appointments,
                "doctor": doctor,
                "unread_map": unread_map
            }
        else:
            context = {
                "page": "home",
                "users": users,
                "chats": chats,
                "patient": patients,
                "doctor": doctor,
                "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0),
                "unread_map": unread_map
            }
        print(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
        return render(request, "chat-doctor.html", context)




@csrf_exempt
@login_required
def profile(request):
    context = {
        "page":"profile",
    }
    return render(request,"chat/profile.html",context)

@csrf_exempt
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_messages(request):
    # Get parameters with default values to avoid KeyError
    last_id = request.POST.get('last_id', 0)
    chat_id = request.POST.get('chat_id', 0)
    
    try:
        last_id = int(last_id)
        chat_id = int(chat_id)
    except (ValueError, TypeError):
        last_id = 0
        chat_id = 0
    
    chats = chatMessages.objects.filter(
        Q(id__gt=last_id) &
        (Q(user_from=request.user.id, user_to=chat_id) | 
         Q(user_from=chat_id, user_to=request.user.id))
    )
    new_msgs = []
    for chat in list(chats):
        data = {}
        data['id'] = chat.id
        data['user_from_id'] = chat.user_from.id
        data['user_to_id'] = chat.user_to.id
        data['message'] = chat.message
        data['date_created'] = chat.date_created.strftime("%b-%d-%Y %H:%M")
        # Add avatar URL for received messages
        if chat.user_from != request.user:
            try:
                if chat.user_from.is_doctor:
                    doctor = Doctor_Information.objects.get(user=chat.user_from)
                    data['user_from_avatar'] = doctor.featured_image.url
                elif chat.user_from.is_patient:
                    patient = Patient.objects.get(user=chat.user_from)
                    data['user_from_avatar'] = patient.featured_image.url
                else:
                    data['user_from_avatar'] = "/static/HealthStack-System/images/Normal/default-avatar.png"
            except:
                data['user_from_avatar'] = "/static/HealthStack-System/images/Normal/default-avatar.png"
        print(data)
        new_msgs.append(data)
    return HttpResponse(json.dumps(new_msgs), content_type="application/json")

@csrf_exempt
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def send_chat(request):
    resp = {}
    User = get_user_model()
    if request.method == 'POST':
        post = request.POST
        
        try:
            u_from = User.objects.get(id=post['user_from'])
            u_to = User.objects.get(id=post['user_to'])
            insert = chatMessages(user_from=u_from, user_to=u_to, message=post['message'])
            insert.save()
            resp['status'] = 'success'
            resp['message_id'] = insert.id
        except User.DoesNotExist:
            resp['status'] = 'failed'
            resp['error'] = 'User not found'
            resp['user_from'] = post.get('user_from')
            resp['user_to'] = post.get('user_to')
        except Exception as ex:
            resp['status'] = 'failed'
            resp['error'] = str(ex)
            import traceback
            resp['traceback'] = traceback.format_exc()
    else:
        resp['status'] = 'failed'
        resp['error'] = 'Invalid request method'

    return HttpResponse(json.dumps(resp), content_type="application/json")


@csrf_exempt
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def check_new_messages(request):
    """Check for new messages for dashboard notifications"""
    resp = {'success': False, 'new_messages': []}
    
    if request.method == 'POST':
        try:
            last_id = int(request.POST.get('last_id', 0))
            user_id = int(request.POST.get('user_id', 0))
            
            # Get new messages where current user is the recipient
            new_messages = chatMessages.objects.filter(
                id__gt=last_id,
                user_to=request.user,
                is_read=False  # Only unread messages for notifications
            ).order_by('date_created')
            
            for msg in new_messages:
                if request.user.is_patient:
                    # For patients, show doctor info
                    message_data = {
                        'id': msg.id,
                        'message': msg.message,
                        'timestamp': msg.date_created.strftime("%b %d, %I:%M %p"),
                        'doctor_id': msg.user_from.id,
                        'doctor_name': f"Dr. {msg.user_from.first_name} {msg.user_from.last_name}"
                    }
                else:
                    # For doctors, show patient info
                    message_data = {
                        'id': msg.id,
                        'message': msg.message,
                        'timestamp': msg.date_created.strftime("%b %d, %I:%M %p"),
                        'patient_id': msg.user_from.id,
                        'patient_name': f"{msg.user_from.first_name} {msg.user_from.last_name}"
                    }
                resp['new_messages'].append(message_data)
            
            resp['success'] = True
            
        except (ValueError, TypeError):
            resp['error'] = 'Invalid parameters'
        except Exception as e:
            resp['error'] = str(e)
    
    return HttpResponse(json.dumps(resp), content_type="application/json")




       