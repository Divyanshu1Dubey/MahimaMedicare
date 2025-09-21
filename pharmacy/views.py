import email
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from hospital.models import Patient
from pharmacy.models import Medicine, Cart, Order
from .utils import searchMedicines
import requests
import base64


@csrf_exempt
@login_required(login_url="login")
def pharmacy_single_product(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        medicines = Medicine.objects.get(serial_number=pk)
        orders = Order.objects.filter(user=request.user, ordered=False)
        carts = Cart.objects.filter(user=request.user, purchased=False)
        if carts.exists() and orders.exists():
            order = orders[0]
            context = {'patient': patient, 'medicines': medicines, 'carts': carts, 'order': order, 'orders': orders}
        else:
            context = {'patient': patient, 'medicines': medicines, 'carts': carts, 'orders': orders}
        return render(request, 'pharmacy/product-single.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


# ...existing imports...

@csrf_exempt
@login_required(login_url="login")
def pharmacy_shop(request):
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        medicines, search_query = searchMedicines(request)
        orders = Order.objects.filter(user=request.user, ordered=False)
        carts = Cart.objects.filter(user=request.user, purchased=False)

        # Normalize category for JS filtering
        for med in medicines:
            raw_cat = med.medicine_category or ""
            normalized = (
                raw_cat.lower()
                .replace(" ", "")
                .replace("/", "")
                .replace("&", "")
                .replace("(", "")
                .replace(")", "")
                .replace("-", "")
                .replace(".", "")
            )
            # Map some common categories to tab values
            mapping = {
                "fever": "fever",
                "pain": "pain",
                "cough": "cough",
                "cold": "cold",
                "flu": "flu",
                "allergy": "allergy",
                "infection": "infection",
                "stomach": "stomach",
                "hypertension": "hypertension",
                "heart": "hypertension",
                "diabetes": "diabetes",
                "skin": "skin",
                "vitamins": "vitamins",
                "eyeearnose": "eye",
                "respiratoryasthmabronchitis": "respiratory",
                "urinary": "urinary",
                "firstaid": "firstaid",
            }
            med.normalized_category = mapping.get(normalized, normalized)

        # Find expiring medicines (within 30 days)
        expiring_medicines = [med for med in medicines if getattr(med, 'is_expiring_soon', False)]

        context = {
            'patient': patient,
            'medicines': medicines,
            'carts': carts,
            'orders': orders,
            'search_query': search_query,
            'expiring_medicines': expiring_medicines
        }
        if orders.exists():
            context['order'] = orders[0]

        return render(request, 'Pharmacy/shop.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')



@csrf_exempt
@login_required(login_url="login")
def cart_view(request):
    if request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        carts = Cart.objects.filter(user=request.user, purchased=False)
        orders = Order.objects.filter(user=request.user, ordered=False)

        if carts.exists() and orders.exists():
            order = orders[0]
            context = {'carts': carts, 'order': order, 'patient': patient}
            return render(request, 'Pharmacy/cart.html', context)
        else:
            messages.info(request, "Your cart is empty.")
            return redirect('pharmacy-shop')
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def add_to_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = get_object_or_404(Medicine, pk=pk)
        
        # Check if item has sufficient unit quantity
        if item.quantity <= 0:
            messages.error(request, f"{item.name} is out of stock.")
            return redirect('pharmacy-shop')
        
        order_item, created = Cart.objects.get_or_create(item=item, user=request.user, purchased=False)
        order_qs = Order.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                # Check if adding one more would exceed unit quantity
                if order_item.quantity + 1 > item.quantity:
                    messages.error(request, f"Cannot add more {item.name}. Only {item.quantity} units left.")
                    return redirect('pharmacy-cart')
                order_item.quantity += 1
                order_item.save()
                messages.info(request, f"{item.name} quantity was updated.")
            else:
                order.orderitems.add(order_item)
                messages.success(request, f"{item.name} was added to your cart.")
        else:
            order = Order.objects.create(user=request.user)
            order.orderitems.add(order_item)
            messages.success(request, f"{item.name} was added to your cart.")

        return redirect('pharmacy-cart')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def remove_from_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                order.orderitems.remove(order_item)
                order_item.delete()
                messages.warning(request, f"{item.name} was removed from your cart.")
            else:
                messages.info(request, "This item was not in your cart.")
        else:
            messages.info(request, "You don't have an active order.")
        return redirect('pharmacy-cart')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def increase_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                # Check if increasing would exceed unit quantity
                if order_item.quantity + 1 > item.quantity:
                    messages.error(request, f"Cannot add more {item.name}. Only {item.quantity} units left.")
                    return redirect('pharmacy-cart')
                order_item.quantity += 1
                order_item.save()
                messages.info(request, f"{item.name} quantity has been updated.")
        return redirect('pharmacy-cart')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


@csrf_exempt
@login_required(login_url="login")
def decrease_cart(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        item = get_object_or_404(Medicine, pk=pk)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.orderitems.filter(item=item).exists():
                order_item = Cart.objects.filter(item=item, user=request.user, purchased=False)[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.info(request, f"{item.name} quantity has been updated")
                else:
                    order.orderitems.remove(order_item)
                    order_item.delete()
                    messages.warning(request, f"{item.name} has been removed from your cart.")
        return redirect('pharmacy-cart')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'patient-login.html')


# PayMongo functions removed - now using Razorpay integration