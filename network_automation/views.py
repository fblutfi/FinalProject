from os import read
from typing import Text
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import Device, Log
from .forms import DeviceFrom, CreateUserForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password , check_password
from django.contrib.auth.models import User
import paramiko
from datetime import datetime
import time



@login_required
def home(request):
    print(request.user.is_authenticated)
    print(request.user,"telah melakukan login")

    template_name = None
    if request.user.is_authenticated:
            #logika untuk user
        template_name = 'home.html'
    else:
            #logika untuk anonymous user
        template_name = 'login.html'

    all_device = Device.objects.all()
    mikrotik_device = Device.objects.filter(vendor='mikrotik')
    last_event = Log.objects.all().order_by('-id')[:10]
    
    context = {
        'all_device': len(all_device),
        'mikrotik_device': len(mikrotik_device),
        'last_event': last_event
    }
    return render(request, template_name, context)

def loginView(request):
    context = {
        'page_title':'LOGIN'
    }
    
    if request.method == "POST":

        username_login = request.POST['username']
        password_login = request.POST['password']
 
        user = authenticate(request, username=username_login, password=password_login)
        
        if user is not None :
            login(request, user)
            return redirect('home')
        else:
            return redirect('login')

    if request.method == "GET":
        if request.user.is_authenticated:
                #logika untuk user
            return redirect('home')
        else:
                #Jika gagal login selalu dilarikan ke halaman login
            return render(request, 'loginv2.html', context)

@login_required
def logoutView(request):
    context = {
        'page_title':'logout'
    }
    if request.method == "POST":
        if request.POST["logout"] == "Submit":
            logout(request)

        return redirect('login')   

    return render(request, 'logout.html', context)

@login_required
def devices(request):
    all_device = Device.objects.all()

    context = {
        'all_device': all_device
    }

    return render(request, 'devices.html', context)

@login_required
def configure(request):
    if request.method == "POST":
        selected_device_id = request.POST.getlist('device')
        mikrotik_command = request.POST['mikrotik_command'].splitlines()
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address,username=dev.username,password=dev.password)
                if dev.vendor.lower() == 'cisco':
                    conn = ssh_client.invoke_shell()
                    conn.send("conf t\n")
                    for cmd in cisco_command:
                        conn.send(cmd + "\n")
                        time.sleep(1)
                else:
                    for cmd in mikrotik_command:
                        ssh_client.exec_command(cmd)

                log = Log(target=dev.ip_address, action="Configure", status="Success", time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action="Configure", status="Error", time=datetime.now(), messages=e)
                log.save()            
        return redirect('home')

    else:
        devices = Device.objects.all()
        context = {
            'devices' : devices,
            'mode' : 'Configure'
        }
        return render(request, 'config.html', context)

@login_required
def verify_config(request):
    if request.method == "POST":
        result = []
        selected_device_id = request.POST.getlist('device')
        mikrotik_command = request.POST['mikrotik_command'].splitlines()
        # cisco_command = request.POST['cisco_command'].splitlines()
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                print(dev)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address,username=dev.username,password=dev.password)

                if dev.vendor.lower() == 'mikrotik':
                    for cmd in mikrotik_command:
                        stdin,stdout,stderr = ssh_client.exec_command(cmd)
                        result.append("Result on {}".format(dev.ip_address))
                        result.append(stdout.read().decode())
                else:    
                    conn = ssh_client.invoke_shell()
                    conn.send('terminal length 0\n')  
                    for cmd in cisco_command:
                        result.append("Result on {}".format(dev.ip_address))
                        conn.send(cmd + "\n")
                        time.sleep(1)
                        output = conn.recv(65535)
                        result.append(output.decode())

                log = Log(target=dev.ip_address, action="Verify Config", status="Success", time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action="Verify Config", status="Error", time=datetime.now(), messages=e)
                log.save()          

        result = '\n'.join(result)
        return render(request, 'verify_result.html', {'result':result})

    else:
        devices = Device.objects.all()
        context = {
            'devices' : devices,
            'mode' : 'Verify Config'
        }
        return render(request, 'verify.html', context)

@login_required
def log(request):
    logs = Log.objects.all().order_by('-time')
    
    context = {
        'logs': logs
    }

    return render(request, 'log.html', context)


@login_required
def create(request):
    form = DeviceFrom()

    if request.method == 'POST':
        form = DeviceFrom(request.POST)
        if form.is_valid():
            form.save()

            return redirect('devices')

    context = {'form':form}

    return render(request, 'tambah.html', context)


@login_required
def update(request, device_id):
    
    updet = Device.objects.get(id=device_id)
    form = DeviceFrom(instance=updet)

    if request.method == 'POST':
        form = DeviceFrom(request.POST, instance=updet)
        if form.is_valid():
            form.save()

            return redirect('devices')

    context = {'form':form}

    return render(request, 'update.html', context)

@login_required
def delete(request, device_id):
    delet = Device.objects.get(id=device_id)
    if request.method == 'POST':
        delet.delete()
        return redirect('devices')

    context = {'item':delet}
    return render(request, 'delete.html', context)


# @login_required
# def usercreate(request):
#     form = CreateUserForm()

#     if request.method == 'POST':
#         form = CreateUserForm(request.POST)
#         if form.is_valid():
#             form.save()

#             return redirect('home')

#     context = {'form':form}

#     return render(request, 'tambah_user.html', context)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def usercreate(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        User.objects.create_user(username, email, password)

        return redirect('home')
    
    return render(request, 'tambah_user.html',{})
            
# delete Log
#     python manage.py shell
# >> from {app_name}.models import {model_name}
# >> {model_name}.objects.all().delete()
