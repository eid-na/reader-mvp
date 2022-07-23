from http.client import HTTPResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
import smartcard
from .forms import PinForm

from smartcard.System import readers
from smartcard.CardMonitoring import CardMonitor
from smartcard.Exceptions import CardRequestTimeoutException
from .apdu import CardObserver, Session, CommandAPDU, ResponseAPDU

session = None

def index(request):
    global session
    if session and request.method == "POST":
        form = PinForm(request.POST)
        if form.is_valid():
            pin = form.cleaned_data['pin']
            
#            if session.tryPin(pin):
#                pass


            return HttpResponse(f"Valid PIN?: {session.tryPin(pin)}")
        else:
            return HttpResponse("Invalid PIN")
    else:
        try:
            session = Session()
        except CardRequestTimeoutException:
            return HttpResponse("Insert your card and refresh the page.")

        form = PinForm()
        return render(request, 'pin.html', {'form': form, 'sc': readers()[0]})

def success(request):
    return HttpResponse("Success")