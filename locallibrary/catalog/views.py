from typing import Any
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import generic
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin
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
