from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Registrar usuario
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password)
            user.save()    
            messages.success(request, 'Conta criada com sucesso') #mensagem apos criacao da conta
            return redirect('login')
    else:          
        form = RegistrationForm()
        
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

# Login Usuario
def login(request):
    if request.method == 'POST':
        identifier = request.POST.get('email', '').strip()  
        password = request.POST.get('password', '')
        user = auth.authenticate(request, username=identifier, password=password)

        if user is None:
            try:
                account = Account.objects.get(email__iexact=identifier)
                user = auth.authenticate(request, username=account.username, password=password)
            except Account.DoesNotExist:
                pass

        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect('home')
            messages.error(request, 'Conta desativada.')
            return redirect('login')

        messages.error(request, 'Usuário ou senha incorretos.')
        return redirect('login')
    
    return render(request, 'accounts/login.html')

# Logout Usuario
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Voce saiu da sua conta.')
    return redirect ('login')