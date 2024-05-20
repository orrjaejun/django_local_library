from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language


#admin.site.register(Book)
#admin.site.register(Author)
admin.site.register(Genre)
#admin.site.register(BookInstance)
admin.site.register(Language)

# Define the admin calss 


class AuthorInline(admin.TabularInline):
        model = Book
        extra = 0

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    inlines = [AuthorInline]
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

# Register admin class with associated model
admin.site.register(Author, AuthorAdmin)


class BookAdmin(admin.ModelAdmin):
    class BookInstanceInline(admin.TabularInline):
        model = BookInstance
        extra = 0
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]
admin.site.register(Book, BookAdmin)

class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')
    list_display = ('book', 'status', 'due_back', 'id')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')}),
        ('Availability', {
            'fields': ('status', 'due_back')
        })
    )
admin.site.register(BookInstance,BookInstanceAdmin)

