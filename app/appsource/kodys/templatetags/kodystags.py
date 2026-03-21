from django import template

register = template.Library()

@register.filter
def font_size(value):
    try:
    	float(value)
    	return "f-12"
    except:
    	return "f-10"

@register.filter
def color(value):
    try:
    	if value == "Y":
    		return "green"
    	else:
    		return "red"
    except:
    	return ""

@register.filter
def vpt_font_size(value):
    try:
        float(value)
        return "f-20"
    except:
        return "f-17"
