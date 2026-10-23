# Docker Cheat Sheet -- NRW Data Center BI

## 🟢 Safe Commands (Daily Use)

### Start services

``` bash
docker compose up
```

### Start in background

``` bash
docker compose up -d
```

### Stop services (keeps database)

``` bash
docker compose stop
```

### Restart services

``` bash
docker compose restart
```

### Running containers

``` bash
docker ps
```

### All containers

``` bash
docker ps -a
```

### Logs

``` bash
docker compose logs
```

### Follow logs

``` bash
docker compose logs -f
```

### PostgreSQL logs

``` bash
docker compose logs postgres
```

### PostgreSQL shell

``` bash
docker exec -it nrw-postgis psql -U postgres -d nrw_dc_bi
```

### Container shell

``` bash
docker exec -it nrw-postgis bash
```

### Volumes

``` bash
docker volume ls
```

### Networks

``` bash
docker network ls
```

### Images

``` bash
docker images
```

### Disk usage

``` bash
docker system df
```

## 🟡 Use With Caution

### Remove containers (database kept)

``` bash
docker compose down
```

### Rebuild

``` bash
docker compose up --build
```

### Pull latest images

``` bash
docker compose pull
```

### Remove container

``` bash
docker rm <container_name>
```

### Remove image

``` bash
docker rmi <image_name>
```

## 🔴 Danger Zone

### Delete containers and database volume

``` bash
docker compose down -v
```

### Delete database volume

``` bash
docker volume rm postgres_data
```

### Delete unused Docker resources

``` bash
docker system prune
```

### Delete everything

``` bash
docker system prune -a --volumes
```

## PostgreSQL Commands

``` sql
\l
\c nrw_dc_bi
\dt
\d facilities
\q
```

## Daily Workflow

``` bash
docker compose up -d
docker ps
docker compose logs -f
docker compose stop
docker compose up -d
```

## Avoid Unless Intentional

``` bash
docker compose down -v
docker volume rm postgres_data
docker system prune -a --volumes
```
