# coding: utf-8

class menuitem:
    def __init__(self, parent, name, url, active = True, template = None):
        self.name = name
        self.url = url
        self.parent = parent
        self.active = active
        self.full_url = self.compute_full_url()
        if template == None:
            self.template = parent.template + ('' if name == '' else '/' + name)
        elif template.startswith('/'):
            self.template = template[1:-1]
        else:
            self.template = parent.template + '/' + template
    
    def compute_full_url(self):
        if self.url.startswith('http'):
            return self.url
        return self.parent.full_url + self.url

class dummymenuitem(menuitem):
    def __init__(self):
        menuitem.__init__(self, rootmenuitem(), name = 'none', url = '')
    
class rootmenuitem(menuitem):
    def __init__(self):
        menuitem.__init__(self, parent = None, name = '', url = '', active = False, template = '/')
    
    def compute_full_url(self):
        return '/'

class globalmenuitem(menuitem):
    def __init__(self, name, url, icon, alt, active = True, template = None):
        menuitem.__init__(self, parent = rootmenuitem(), name = name, url = url, active = active, template = template)
        self.icon = icon
        self.alt = alt

class contentmenuitem(menuitem):
    def __init__(self, parent, name, url, text, visible = True, cols = 3, template = None):
        menuitem.__init__(self, parent, name, url, template = template)
        self.text = text
        self.cols = cols
        self.visible = visible

def find_active_item(path, items):
    best_fit = None
    for item in items:
        if path == item.url.rstrip('/') or path.startswith(item.url):
            if best_fit is None or len(item.url) > len(best_fit.url):
                best_fit = item
    return best_fit or dummymenuitem()
    
def menu(path):
    global_menu = [
        globalmenuitem(name = 'home',    url = '',  icon = 'icon-yoursway.png', template = 'index', alt = 'Home'),
        globalmenuitem(name = '*',    url = '*',  icon = 'icon-yoursway.png', template = 'index_int', alt = 'Home'),
        # globalmenuitem(name = 'users',    url = 'helps/users/',  icon = 'icon-yoursway.png', template = 'index_int', alt = 'Home'),
        # # globalmenuitem(name = 'consulting', url = 'consulting/', icon = 'icon-consulting.png',  alt = 'Consulting'),
        # globalmenuitem(name = 'consulting', url = '', icon = 'icon-yoursway.png',  alt = 'YourSway'),
        # # globalmenuitem(name = 'ide',     url = 'ide/', active = False, icon = 'icon-ide.png',      alt = 'YourSway IDE'),
        # # globalmenuitem(name = 'taskus',  url = 'taskus/',  icon = 'icon-taskus.png',   alt = 'Taskus'),
        # globalmenuitem(name = 'free', url = 'free/', icon = 'icon-free.png',  alt = 'Free Tools'),
        # globalmenuitem(name = 'aboutus', url = 'aboutus/', icon = 'icon-aboutus.png',  alt = 'About Us'),
        # globalmenuitem(name = 'blog', url = 'http://blog.yoursway.com/', icon = 'icon-blog.png',  alt = 'Blog'),
    ]
    
    path = path.lstrip('/')
    
    active_global_item = global_menu[0] if path=='index' else global_menu[1] # find_active_item(path, global_menu)
    path = path[len(active_global_item.url) : -1]
    
    if active_global_item.name == 'taskus':
        content_menu = [
            contentmenuitem(parent = active_global_item, name = '', url = '', template = 'overview', text = "5 easy rules", cols = 4),
            contentmenuitem(parent = active_global_item, name = 'screencast', url = 'screencast/', text = 'Screencast', cols = 4),
            contentmenuitem(parent = active_global_item, name = 'qa', url = 'qa/', text = 'Productivity Q&A', cols = 6),
            contentmenuitem(parent = active_global_item, name = 'support', url = 'support/', text = 'Support', cols = 4),
        ]
    elif active_global_item.name == 'free':
        content_menu = [
        contentmenuitem(parent = active_global_item, name = '', url = '', template = 'overview', text = "Overview", cols = 4),
        contentmenuitem(parent = active_global_item, name = 'ProjectSync', url = 'ProjectSync/', text = 'ProjectSync', cols = 4),
        # contentmenuitem(parent = active_global_item, name = 'ide-features', url = 'ide/features', text = '', visible = False),
        # contentmenuitem(parent = active_global_item, name = 'mashups', url = 'mashups/', text = 'Desktop & Web app', cols = 7),
        # contentmenuitem(parent = active_global_item, name = 'iphone', url = 'iphone/', text = 'iPhone app', cols = 4),
        ]
    elif active_global_item.name == 'consulting':
        content_menu = [
        contentmenuitem(parent = active_global_item, name = '', url = '', template = 'overview', text = "Overview", cols = 4),
        contentmenuitem(parent = active_global_item, name = 'ide', url = 'ide/', text = 'I want an IDE', cols = 5),
        contentmenuitem(parent = active_global_item, name = 'ide-features', url = 'ide/features', text = '', visible = False),
        contentmenuitem(parent = active_global_item, name = 'mashups', url = 'mashups/', text = 'Desktop & Web app', cols = 7),
        contentmenuitem(parent = active_global_item, name = 'iphone', url = 'iphone/', text = 'iPhone app', cols = 4),        ]
    else:
        content_menu = []
        
    remaining_content_menu_cols = 23 - sum([item.cols for item in content_menu if item.visible])

    active_content_item = find_active_item(path, content_menu)
    if isinstance(active_content_item, dummymenuitem):
        active_item = active_global_item
    else:
        active_item = active_content_item
        
    visible_content_menu_items = [item for item in content_menu if item.visible]

    return (active_item, dict(global_menu = global_menu,
        content_menu = visible_content_menu_items,
        active_global_item = active_global_item.name,
        active_content_item = active_content_item.name,
        remaining_content_menu_cols = remaining_content_menu_cols,
    ))
