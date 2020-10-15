"""Application 'posts' context processors."""
import datetime as dt


def year(request):
    """Return current year."""
    now_year = dt.datetime.now().year
    return {
        'now_year': now_year,
    }
