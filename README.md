to start a container localy run

docker compose up

to run dev env container (env.dev required)
docker compose -f docker-compose.dev.yml up -d --build

to apply migrations on dev azure postgress
docker compose -f docker-compose.dev.yml exec api alembic upgrade head

to generate migration from container 
 docker compose exec api alembic revision --autogenerate -m "some message"

to apply migration localy
 docker compose exec api alembic upgrade head