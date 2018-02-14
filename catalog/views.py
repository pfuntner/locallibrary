from django.shortcuts import render, redirect

from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group

def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    # num_books=Book.objects.all().count()
    num_books=Book.objects.count()
    num_instances=BookInstance.objects.count()
    # Available books (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0) + 1
    request.session['num_visits'] = num_visits

    """
    user = str(request.user)
    if user == "AnonymousUser":
        user = "guest"
    """

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={
            'num_books':num_books,
            'num_instances':num_instances,
            'num_instances_available':num_instances_available,
            'num_authors':num_authors,
            'num_visits': num_visits,
            # 'user': user,
        },
    )

class BookListView(generic.ListView):
    model = Book
    paginate_by = 5

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 3

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

def isLibrarian(user):
    group = Group.objects.get(name='Librarians')
    return group and (group in user.groups.all())


class AllOnLoanListView(LoginRequiredMixin, generic.ListView):
    """
    Allow librarians (staff members) to see:
      - all books on loan
      - names of borrowers
    """
    model = BookInstance
    template_name = 'catalog/all_onloan_books.html'
    paginate_by = 10

    def get(self, *args, **kwargs):
        if not isLibrarian(self.request.user):
            return redirect("denied")
        else:
            return super(AllOnLoanListView, self).get(*args, **kwargs)

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

def denied(request):

    return render(
        request,
        'denied.html')
