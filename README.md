ws4dmwm
=======

Web-sockets implementation for CMS DMWM framework. This repository contains
working code examples which shows how to implement web-socket framework [1]
into DMWM web framework.

The missing part is front-end proxy. The NGINX server has dedicated proxy
module [2] for that, while apache server proxy module [3] is still under
development. The CMS experiment relies on apache for front-end, so we need to
wait for apache proxy module implementation.

Reference:
----------

[1] https://github.com/Lawouach/WebSocket-for-Python
[2] https://github.com/yaoweibin/nginx_tcp_proxy_module
[3] https://github.com/disconnect/apache-websocket
