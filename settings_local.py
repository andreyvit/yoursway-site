# -*- encoding: utf-8 -*-

DATABASE_ENGINE = 'sqlite3' # variants: mysql, sqlite3
DATABASE_NAME = '/srv/www/yoursway.com/mainsite/blog.db'
DATABASE_USER = ''
DATABASE_PASSWORD = ''

SERVER_EMAIL = 'blog@yoursway.com'

FORCE_SCRIPT_NAME = ''

BLOG_NAME = u'Yoursway Blog'
TAGLINE = u''
FOOTER = u'(c) 2007-2008 <a href="/">YoursWay LLC</a>'

DEFAULT_FROM_EMAIL = '%s <blog@yoursway.com>' % BLOG_NAME

# You may place templates for rendering HTML to the ../themes/{{ THEME }}/ directory.
# They will override the templates with the same name from ../templates/ directory.
THEME = 'default'

# Sample static pages links
STATIC_PAGES = (
)

# Set this to true to get first comment by any user autoapproved
# This makes sense if captcha is enabled
ANONYMOUS_COMMENTS_APPROVED = False

# Possible choices are: ''|'simple'|'recaptcha'
# To utilize recaptcha you must get public/private keys
# from http://recaptcha.net/
CAPTCHA='simple'
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY =''

ENABLE_SAPE = False # Set this to true to enable Sape.ru client
ENABLE_IMPORT = False # Set this to true to enable WordPress importer
GA_ACC = '' # Google Analytics account
LI_ACC = False # Set True if you want liveinternet.ru counter
GRAVATAR_ENABLE = False # Enable gravatars?
SHORT_POSTS_IN_FEED = False # Full or short posts in feed
WYSIWYG_ENABLE = True # WYSIWYG for post text in admin
RENDER_METHOD = 'markdown' # Choices: bbcode and simple. Don't use html here, it is unsafe

# SOCIAL_BOOKMARKS can be reconfigured to contain values from apps/blog/templatetags/bookmarks.py
# BLOG_URLCONF_ROOT can be set if you want to remove 'blog/' prefix
# URL_PREFIX can be set to add url prefix to *all* urls

# Livejournal crossposting
ENABLE_LJ_CROSSPOST = False
LJ_USERNAME = ''
LJ_PASSWORD = ''

# DEBUG must be False in production mode
# Please read http://byteflow.su/wiki/DEBUG
DEBUG = False

# Set it to True if you want to activate orm_debug template tag
# You also need to setup INTERNAL_IPS setting 
# if you want to use explain feature of orm_debug
ORM_DEBUG = False
