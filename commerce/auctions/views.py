from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms

from datetime import datetime

from .models import User, Listing, Bid, Category, Watchlist, Comment
from . import util


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'category', 'photo']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.CheckboxSelectMultiple,
            'photo': forms.URLInput(attrs={'class': 'form-control'})
        }


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        labels = {
            "amount": "Place a Bid"
        }


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def new_listing(request):
    if request.method == "POST":
        # Retrieve form data, check for validity
        # Then retrieve logged-in user before saving
        form = ListingForm(request.POST)
        if form.is_valid():
            # Before saving listing, retrieve current user
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            # Saves category after saving to database
            form.save_m2m()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new_listing.html", {
                "form": form
            })
    else:
        return render(request, "auctions/new_listing.html", {
            "form": ListingForm()
        })


def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    # Function in util.py searches for highest bid for listing
    highest_bid = util.find_bid(listing_id)
    if not highest_bid:
        highest_bid = "No Bids"

    # Find if item in user watchlist, if false it's not, if true it is
    if request.user.is_authenticated:
        in_watchlist = util.find_list(listing_id, request.user)
    else:
        in_watchlist = False

    # Find if logged in user is the owner of the listing
    if request.user == listing.seller:
        owner = True
    else:
        owner = False

    # Retrive all comments for listing, send through to template
    comments = Comment.objects.filter(listing=listing_id)

    # If listing is no longer active, display message
    if not listing.active:
        # Find out who the winner was
        winning_bid = Bid.objects.get(listing=listing_id, amount=highest_bid)
        winner = winning_bid.bidder
        # If user logged in is winner, display winner message
        if winner == request.user:
            message = "You've won this item!"
        # Otherwise, display ended message
        else:
            message = "This auction has ended."
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "highest_bid": highest_bid,
            "form": BidForm(),
            "watchlist": in_watchlist,
            "owner": owner,
            "message": message,
            "active": listing.active,
            "comments": comments
        })

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "highest_bid": highest_bid,
            "form": BidForm(),
            "watchlist": in_watchlist,
            "owner": owner,
            "active": listing.active,
            "comments": comments
            })


def bid(request, listing_id):
    if request.method == "POST":
        # Retrieve bid from form
        form = BidForm(request.POST)
        if form.is_valid():
            listing = Listing.objects.get(id=listing_id)
            # Function in util.py searches for highest bid for listing
            highest_bid = util.find_bid(listing_id)

            # If no current highest bid, must be first bid
            if not highest_bid:
                # Check if entered bid is at least as high as starting_bid
                if form.cleaned_data['amount'] >= listing.starting_bid:
                    bid = form.save(commit=False)
                    bid.bidder = request.user
                    bid.listing = listing
                    bid.save()
                    return redirect('listing', listing_id=listing_id)
                else:
                    return render(request, "auctions/invalid.html", {
                        "message": "Bid must be higher than starting bid or current bid."
                    })

            # Check if new bid is greater than current highest
            else:
                if form.cleaned_data['amount'] > highest_bid:
                    bid = form.save(commit=False)
                    bid.bidder = request.user
                    bid.listing = listing
                    bid.save()
                    return redirect('listing', listing_id=listing_id)
                else:
                    return render(request, "auctions/invalid.html", {
                        "message": "Bid must be higher than starting bid or current bid."
                    })


"""
This view is for adding and removing listings from user watchlist
"""
def watchlist(request, listing_id):
    if request.method == "POST":
        # If submit value is Add to Watchlist, listing will be added
        if request.POST['watchlist'] == "Add to Watchlist":
            listing = Listing.objects.get(id=listing_id)
            add_list = Watchlist.objects.create(owner=request.user, listing=listing)
            return redirect('listing', listing_id=listing_id)
        # Otherwise, the value will be Remove from Watchlist, and upon submit listing
        # will be deleted from watchlist
        else:
            Watchlist.objects.filter(owner=request.user, listing=listing_id).delete()
            return redirect('listing', listing_id=listing_id)


"""
This view is for retrieving and rendering the user's watchlist
"""
def view_watchlist(request):
    # Retrieve user watchlist by iterating over watchlist database and getting associated listing
    # Likely could have used related_name to do this, but trying to do that took more time than it was worth
    user_watchlist = list(Watchlist.objects.filter(owner=request.user))
    listings = []
    # Add all listings on user's watchlist to a list
    for i in range(len(user_watchlist)):
        listings.append(Listing.objects.get(title=user_watchlist[i].listing))

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def close(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        # Change active from True to False to mark listing as closed
        listing.active = False
        listing.save()

        return redirect('listing', listing_id=listing_id)


def comment(request, listing_id):
    if request.method == "POST":
        # Add comment to database
        comment = request.POST["comment_text"]
        commenter = request.user
        listing = Listing.objects.get(id=listing_id)
        new_comment = Comment.objects.create(listing=listing, commenter=commenter, comment=comment)

        return redirect('listing', listing_id=listing_id)


"""
This view is for the page listing all the categories
"""
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


"""
This view is for the individual category pages and their respective listings
"""
def category(request, category):
    category = Category.objects.get(category=category)
    listings = Listing.objects.filter(category=category, active=True)
    return render(request, "auctions/category_page.html", {
        "listings": listings,
        "category": category
    })
