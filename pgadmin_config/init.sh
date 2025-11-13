#!/bin/sh

# Создаем директорию для пользователя если её нет
mkdir -p /var/lib/pgadmin/storage/admin_health-assist.com

# Копируем pgpass файл в нужное место
cp /pgadmin4/pgpass /var/lib/pgadmin/storage/admin_health-assist.com/pgpass

# Устанавливаем правильные права
chmod 600 /var/lib/pgadmin/storage/admin_health-assist.com/pgpass
chown pgadmin:pgadmin /var/lib/pgadmin/storage/admin_health-assist.com/pgpass

# Запускаем pgAdmin
/entrypoint.sh