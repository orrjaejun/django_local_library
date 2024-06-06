import datetime
from typing import Any
from django.db.models.query import QuerySet
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from catalog.forms import RenewBookModelForm
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from .forms import RentBookForm

#Book View Classes
class BookListView(generic.ListView):
    model: Book
    paginate_by = 5
    context_object_name = "book_list"
    queryset = Book.objects.all()
    template_name = 'books/my'

class BookDetailView(generic.DetailView):
    model = Book
    
    def book_detail_view(request, primary_key):
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise Http404('Book does not exist')

        return render(request, 'catalog/book_detail.html', context={'book': book})

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

class LoanedBooksAll(UserPassesTestMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/borrowed.html'
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return render(self.request, 'catalog/permission_denied.html', status=403)
        else:
            return redirect('login')

class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    
class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']   

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

#Author View Classes
class AuthorListView(generic.ListView):
    model : Author
    paginate_by : 5
    
    context_object_name = "author_list"
    queryset = Author.objects.all()
    template_name = 'author/my'
    
class AuthorDetailView(generic.DetailView):
    model = Author
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(author=self.get_object())
        return context
    
class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}
    
class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    
class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of Genre
    num_genre = Genre.objects.all().count()

    #view counts
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    

    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genre': num_genre,
        'num_visits' : num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

#reset view counts
def reset_num_visits(request):
        if 'num_visits' in request.session:
            del request.session['num_visits']
        return redirect('index')
    

#Update feature for staff member
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


#Rent book
def rent_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk, status='a')
    
    if request.method == 'POST':
        form = RentBookForm(request.POST)
        if form.is_valid():
            due_back = form.cleaned_data['due_back']
            user = request.user
            # Update the book instance status to indicate it is rented
            book_instance.status = 'o'  # Assuming 'o' means on loan
            book_instance.borrower = user
            book_instance.due_back = due_back
            book_instance.save()
            return render(request, 'catalog/rent_success.html', {'book_instance': book_instance})
        else:
            return render(request, 'catalog/book_rent_fail.html', {'form': form, 'book_instance': book_instance})
    else:
        form = RentBookForm()

    context = {
        'book_instance': book_instance,
        'form': form,
    }

    return render(request, 'catalog/rent.html', context)
