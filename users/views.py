from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def register(request):
    """Register a new user."""
    
    if request.method != 'POST':
        # View an empty registration form
        form = UserCreationForm()
        
    else:
        # Process the filled in form
        form = UserCreationForm(data=request.POST)
        
        if form.is_valid():
            new_user = form.save()
            # Log the user in and redirect to home page.
            login(request, new_user)
            return redirect('happy_cherries:index')
    # Display a blank form
    context = {'form': form}
    return render(request, 'registration/register.html', context)