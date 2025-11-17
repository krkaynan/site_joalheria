from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'cpf', 'cep', 'address', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'order_note']