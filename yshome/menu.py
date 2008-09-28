
class menuitem:
    def __init__(self, parent, name, url, active = True):
        self.name = name
        self.url = url
        self.parent = parent
        self.active = active
        self.full_url = self.compute_full_url()
    
    def compute_full_url(self):
        if self.url.startswith('http'):
            return self.url
        if self.parent == None:
            return '/' + self.url
        else:
            return self.parent.full_url + self.url

class dummymenuitem(menuitem):
    def __init__(self):
        menuitem.__init__(self, None, name = 'none', url = '')

class globalmenuitem(menuitem):
    def __init__(self, name, url, icon, alt, active = True):
        menuitem.__init__(self, parent = None, name = name, url = url, active = active)
        self.icon = icon
        self.alt = alt

class contentmenuitem(menuitem):
    def __init__(self, parent, name, url, text):
        menuitem.__init__(self, parent, name, url)
        self.text = text

def find_active_item(path, items):
    best_fit = None
    for item in items:
        if path == item.url.rstrip('/') or path.startswith(item.url):
            if best_fit is None or len(item.url) > len(best_fit.url):
                best_fit = item
    return best_fit or dummymenuitem()
    
def menu(path):
    global_menu = [
        globalmenuitem(name = 'home',    url = '',         icon = 'icon-yoursway.png', alt = 'Home'),
        globalmenuitem(name = 'ide',     url = 'ide/', active = False, icon = 'icon-ide.png',      alt = 'YourSway IDE'),
        globalmenuitem(name = 'taskus',  url = 'taskus/',  icon = 'icon-taskus.png',   alt = 'Taskus'),
        globalmenuitem(name = 'free', url = 'free/', icon = 'icon-free.png',  alt = 'Free Tools'),
        globalmenuitem(name = 'consulting', url = 'consulting/', icon = 'icon-consulting.png',  alt = 'About Us'),
        globalmenuitem(name = 'aboutus', url = 'aboutus/', icon = 'icon-aboutus.png',  alt = 'About Us'),
        globalmenuitem(name = 'blog', url = 'http://blog.yoursway.com/', icon = 'icon-blog.png',  alt = 'Blog'),
    ]
    
    path = path.lstrip('/')
        
    active_global_item = find_active_item(path, global_menu)
    path = path[len(active_global_item.url) : -1]
    
    if active_global_item.name == 'taskus':
        content_menu = [
            contentmenuitem(parent = active_global_item, name = '', url = '', text = "5 easy rules"),
            contentmenuitem(parent = active_global_item, name = 'screencast', url = 'screencast/', text = 'Screencast'),
            contentmenuitem(parent = active_global_item, name = 'qa', url = 'qa/', text = 'Productivity Q&A'),
            contentmenuitem(parent = active_global_item, name = 'support', url = 'support/', text = 'Support'),
        ]
    else:
        content_menu = []

    active_content_item = find_active_item(path, content_menu)

    return dict(global_menu = global_menu,
        content_menu = content_menu,
        active_global_item = active_global_item.name,
        active_content_item = active_content_item.name,
    )
