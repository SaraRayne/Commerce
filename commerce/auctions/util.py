from .models import User, Listing, Bid, Watchlist
from decimal import *

def find_bid(listing_id):
    """
    Returns highest bid for given listing
    """
    all_bids = list(Bid.objects.filter(listing=listing_id))
    bid_list = []
    for i in range(len(all_bids)):
        bid_list.append(all_bids[i].amount)
    if not bid_list:
        return False
    else:
        highest_bid = max(bid_list)

        return highest_bid


def find_list(listing_id, user):
    """
    Returns true or false based on whether user has
    listing in their watchlist or not
    """
    user_watchlist = Watchlist.objects.filter(owner=user, listing=listing_id)
    if not user_watchlist:
        return False
    else:
        return True
