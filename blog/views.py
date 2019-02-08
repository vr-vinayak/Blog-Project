from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import (TemplateView,ListView,
                                    DetailView,CreateView,
                                    UpdateView,DeleteView)

from blog.models import Post,Comment,UserProfileInfo
from django.utils import timezone

from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout

from blog.forms import PostForm,CommentForm,UserForm,UserProfileInfoForm
from django.urls import reverse_lazy
# Create your views here.

class AboutView(TemplateView):
    template_name='about.html'

#Home Page
class PostListView(ListView):
    model=Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by("-published_date")

#Post Detail
class PostDetailView(DetailView):
    model=Post


class CreatePostView(LoginRequiredMixin,CreateView):
    login_url='/login/'
    redirect_field_name='blog/post_detail.html'
    form_class=PostForm
    model=Post

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url='/login/'
    redirect_field_name='blog/post_detail.html'
    form_class=PostForm
    model=Post


class PostDeleteView(LoginRequiredMixin,DeleteView):
    model=Post
    success_url=reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin,ListView):
    login_url='/login/'
    redirect_field_name='blog/post_list.html'
    model=Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')

#####################################################################
#####################################################################
@login_required
def post_publish(request,pk):
    post=get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail',pk=pk)



@login_required
def add_comment_to_post(request,pk):
    post=get_object_or_404(Post,pk=pk)
    if request.method=='POST':
        form=CommentForm(request.POST)
        if form.is_valid():
            comment=form.save(commit=False)
            comment.post=post
            comment.save()
            return redirect('post_detail',pk=post.pk)
    else:
        form=CommentForm()
    return render(request,'blog/comment_form.html',{'form':form})


@login_required
def comment_approve(request,pk):
    comment=get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('post_detail',pk=comment.post.pk)




@login_required
def comment_remove(request,pk):
    comment=get_object_or_404(Comment,pk=pk)
    post_pk=comment.post.pk
    comment.delete()
    return redirect('post_detail',pk=post_pk)

def register(request):

        registered=False

        if request.method == 'POST':
            user_form=UserForm(data=request.POST)
            profile_form=UserProfileInfoForm(data=request.POST)


            if user_form.is_valid() and profile_form.is_valid():


                user=user_form.save()
                user.set_password(user.password)
                user.save()

                profile=profile_form.save(commit=False)
                profile.user=user

                if 'profile_pic' in request.FILES:
                    profile.profile_pic=request.FILES['profile_pic']
                profile.save()

                registered=True

            else:
                print(user_form.errors,profile_form.errors)
        else:

            user_form=UserForm()
            profile_form=UserProfileInfoForm()

        return render(request,'registrations/registration.html',
                                                    {'user_form':user_form,
                                                    'profile_form':profile_form,
                                                    'registered':registered})

def user_login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('post_list'))
            else:
                return HttpResponse("ACCOUNT IS NOT ACTIVE")
        else:
            print("SOMEONE TRIED TO LOGIN AND FAILED")
            print("Username: {} Password: {}".format(username,password))
            return HttpResponse("Invalid credential provided")

    else:
        return render(request,'registrations/login.html',{})
