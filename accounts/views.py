from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.views.generic.edit import FormView
from .forms import RegisterForm, LoginForm, Socialreg
from .models import *
from django.urls import reverse_lazy, reverse
from django.db import IntegrityError
from django.conf import settings



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save()
                user.is_approved = True
                user.save()
                
                messages.success(request, "✅ Registration successful. You can now login.")
                return redirect('log')  # Redirect to login page
                
            except Exception as e:
                print(f"Registration error: {e}")
                messages.error(request, "An error occurred during registration. Please try again.")
        else:
            print("Form errors:", form.errors)
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})
def social_registration_view(request):
    user = request.user
    return redirect('home')
# class LoginView(FormView):
#     template_name = 'login.html'
#     form_class = LoginForm
#     success_url = reverse_lazy('home') 
#     def form_valid(self, form):
#         uname = form.cleaned_data.get('username')
#         pswd = form.cleaned_data.get('password')
#         from django.contrib.auth import get_user_model
#         User = get_user_model()
#         try:
#             user_obj = User.objects.get(username=uname)
#         except User.DoesNotExist:
#             messages.error(self.request, "Invalid username or password.")
#             return self.form_invalid(form)
#         if not user_obj.is_active and getattr(user_obj, "deletion_reason", None):
#             messages.error(
#                 self.request,
#                 f"Your account has been deleted. Reason: {user_obj.deletion_reason}"
#             )
#             return self.form_invalid(form)
#         user = authenticate(self.request, username=uname, password=pswd)
#         if user:
#             if user.is_superuser:
#                 messages.error(self.request, "Please login via the admin panel.")
#                 return self.form_invalid(form)
#             if hasattr(user, 'deletion_reason') and user.deletion_reason:
#                 messages.error(
#                     self.request,
#                     f"🚫 Your account has been deleted. Reason: {user.deletion_reason}. "
#                     "Please contact support at 📧 stayfinder@gmail.com"
#                 )
#                 return self.form_invalid(form)
#             login(self.request, user)
#             messages.success(self.request, "Login successful.")
#             return redirect('home')
#         else:
#             messages.error(self.request, "Invalid username or password.")
#             return self.form_invalid(form)
#     def get_success_url(self):
#         return reverse('home')
class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        uname = form.cleaned_data.get('username')
        pswd = form.cleaned_data.get('password')

        # ✅ Use hardcoded login
        if uname == 'testuser@gmail.com' and pswd == '12345678':
            self.request.session['user'] = uname
            messages.success(self.request, "Login successful!")
            return redirect('home')
        
        messages.error(self.request, "Invalid username or password.")
        return self.form_invalid(form)
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('log')
