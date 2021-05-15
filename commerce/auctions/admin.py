from django.contrib import admin
from .models import User, Listing, Bid, Category, Watchlist, Comment

class ListingAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(Watchlist)
admin.site.register(Comment)
