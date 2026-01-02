from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChatMessageForm
from .models import ChatThread
from providers.models import Provider


@login_required
def start_provider_chat(request, provider_id):
    if request.user.is_provider() or request.user.is_admin():
        messages.error(request, 'Faqat mijozlar uchun.')
        return redirect('services:home')

    provider = get_object_or_404(Provider, pk=provider_id)
    thread, _ = ChatThread.objects.get_or_create(
        provider=provider,
        client=request.user,
        listing=None,
        defaults={'status': ChatThread.Status.OPEN},
    )
    return redirect('chat:thread_detail', pk=thread.pk)


@login_required
def thread_detail(request, pk):
    thread = get_object_or_404(ChatThread, pk=pk)

    if not (
        request.user.is_admin()
        or thread.provider.user == request.user
        or (thread.client and thread.client == request.user)
    ):
        messages.error(request, 'Ruxsat yo‘q.')
        return redirect('services:home')

    if request.user.is_admin() and thread.admin is None:
        thread.admin = request.user
        thread.save()

    form = ChatMessageForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        message = form.save(commit=False)
        message.thread = thread
        message.sender = request.user
        message.save()
        return redirect('chat:thread_detail', pk=thread.pk)

    return render(request, 'chat/thread_detail.html', {'thread': thread, 'form': form})

# Create your views here.
