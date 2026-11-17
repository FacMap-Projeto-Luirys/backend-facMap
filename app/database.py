from prisma import Prisma

# Cliente único do Prisma; conectado/desconectado no ciclo de vida do app (app/main.py).
db = Prisma()
