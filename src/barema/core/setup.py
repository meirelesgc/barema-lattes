import subprocess
import sys


def setup_database():
    try:
        print("Iniciando banco de dados")
        subprocess.run(["docker", "compose", "up", "barema_db", "-d"], check=True)

        print("Executando migrações")
        subprocess.run(["poetry", "run", "alembic", "upgrade", "head"], check=True)

        print("Iniciando seeding")
        hop_command = [
            "docker",
            "compose",
            "run",
            "--rm",
            "-e",
            "HOP_FILE_PATH=$${PROJECT_HOME}/workflows/Seeding.hwf",
            "barema_hop",
        ]
        subprocess.run(hop_command, check=True)

        print("Fim da execução")

    except subprocess.CalledProcessError as e:
        print(f"Falha na execução. Código de saída: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("Comando não encontrado no sistema.")
        sys.exit(1)
