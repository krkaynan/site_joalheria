from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode
import os
from email.mime.image import MIMEImage

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
            domain = current_site.domain if hasattr(current_site, "domain") else str(current_site)
            mail_subject = 'Por favor ative sua conta'
            context = {
                'user': user,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
            html_message = render_to_string('accounts/account_verification_email.html', context)
            text_message = strip_tags(html_message)
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@seusite.com")
            to_email = email
            msg = EmailMultiAlternatives(mail_subject, text_message, from_email, [to_email])
            msg.attach_alternative(html_message, "text/html")
            msg.send()

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

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Por favor informe um e-mail.')
            return redirect('forgotPassword')

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # uid / token
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # domain: transformamos current_site num string (evita passar objeto)
            current_site = get_current_site(request)
            domain = current_site.domain if hasattr(current_site, 'domain') else str(current_site)

            # Monta o contexto e renderiza o template HTML (use your template path)
            context = {
                'user': user,
                'domain': domain,
                'uid': uidb64,
                'token': token,
            }
            html_message = render_to_string('accounts/reset_password_email.html', context)
            text_message = strip_tags(html_message)

            mail_subject = 'Redefina sua senha'
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@seusite.com')
            to_email = email

            # cria multipart (text + html)
            msg = EmailMultiAlternatives(mail_subject, text_message, from_email, [to_email])
            msg.attach_alternative(html_message, "text/html")

            try:
                msg.send()
            except Exception as e:
                messages.error(request, 'Erro ao enviar o e-mail. Tente novamente mais tarde.')
                return redirect('forgotPassword')
            messages.success(request, 'Um link para redefinir sua senha foi enviado para o seu e-mail.')
            return redirect('login')
        
        else:
            messages.error(request, 'Conta não existente')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')
  

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None 
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Resete sua senha')
        return redirect ('resetPassword')
    else:
        messages.error(request, 'Esse link está expirado')
        return redirect ('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        uid = request.session.get('uid')
        user = Account.objects.get(pk=uid)
        user.set_password(password)
        user.save()
        messages.success(request, 'Sua senha foi redefinida com sucesso!')
        return redirect('login')
    else:
        return render(request, 'accounts/resetPassword.html')