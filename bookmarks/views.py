from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import logout
from bookmarks.forms import *
from bookmarks.models import *

def main_page(request):
    context = {'user': request.user,}
    return render(request, 'bookmarks/main_page.djhtml', context)

def user_page(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        raise Http404('Requested user not found.')
    bookmarks = user.bookmark_set.all()
    template = loader.get_template('user/user_page.djhtml')
    context = {
        'username': username,
        'bookmarks': bookmarks
    }

    return HttpResponse(template.render(context, request))

#def login_page(request):
    

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/register/success')
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'registration/register.djhtml', context)

def bookmark_save_page(request):
    if request.method == 'POST':
        form = BookmarkSaveForm(request.POST)
        if form.is_valid():
            # Create or get link.
            link, dummy = Link.objects.get_or_create(
                url=form.cleaned_data['url']
            )
            # Create or get bookmark.
            bookmark, created = Bookmark.objects.get_or_create(
                user=request.user,
                link=link
            )
            # Update bookmark title.
            bookmark.title = form.cleaned_data['title']
            # If the bookmark is being update, clear old tag list.
            if not created:
                bookmark.tag_set.clear()
            # Create new tag list.
            tag_names = form.cleaned_data['tags'].split()
            for tag_name in tag_names:
                tag, dummy = Tag.objects.get_or_create(name=tag_name)
                bookmark.tag_set.add(tag)
            # Save bookmark to database.
            bookmark.save()
            return HttpResponseRedirect(
                '/user/%s/' % request.user.username
            )
        else:
            form = BookmarkSaveForm()
        context = {'form': form}
        return render(request, 'bookmark_save.djhtml', context)
                
