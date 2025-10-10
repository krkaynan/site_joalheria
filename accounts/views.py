from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

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
            
            # Verificação de conta por email
            current_site = get_current_site(request)
            mail_subject = 'Por favor ative sua conta'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Obrigado por se registrar! Verifique seu e-mail para ativar sua conta.')
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
                return redirect('dashboard')
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

@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Parabéns! Sua conta foi ativada.')
        return redirect('login')
    else:
        messages.error(request, 'Link de ativação invalido.')
        return redirect('register')
        