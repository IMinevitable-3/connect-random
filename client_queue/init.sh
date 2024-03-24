#!/bin/sh

# ( sleep 10 ; \
# rabbitmqctl add_user user password ; \
# rabbitmqctl set_user_tags user administrator ; \
# rabbitmqctl set_permissions -p / user  ".*" ".*" ".*" ; \
(echo "*** User 'guest' with password 'guest' completed. ***" ; \
echo "*** Log in the WebUI at port 15672 (example: http:/localhost:15972) ***") &

rabbitmq-server $@