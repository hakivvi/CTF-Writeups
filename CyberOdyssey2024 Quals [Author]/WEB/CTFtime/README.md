# Details

in `frontend/index.js`, a controlled string directly intrerpolated into the server sidee request path, but it checks for `../` and `..\`, `fetch()/URL()` as many other url parsers remove unsafe characters from urls such as `\t`, `\r`, so something like `..\r/..\r/` would do the trick.