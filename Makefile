all: localecompile

localegen:
	django-admin makemessages -l de

localecompile:
	django-admin compilemessages
