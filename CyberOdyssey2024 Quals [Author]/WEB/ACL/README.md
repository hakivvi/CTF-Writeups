# Details

bypass the `ACL` check using scientific notation, but since i forgot to restrict the json field to ints only, you can also use something like `"1A"`:

```js
> 3e-100 < 1
true
> parseInt(3e-100)
3
> 
```

then RCE by controlling `render()` options, `NODE_ENV` is `prod` so template cache is ON, but you can still turn off the cache: https://blog.huli.tw/2023/06/22/en/ejs-render-vulnerability-ctf/#cache-issue