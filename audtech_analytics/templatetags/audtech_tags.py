
import calendar
from django import template

register = template.Library()

@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]
@register.filter
def week_name(week_number):
    WeekDay={1:"Sunday",6:"Friday",7:"Saturday"}
    return WeekDay.get(week_number)