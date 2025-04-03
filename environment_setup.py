import os
from pathlib import Path
from dotenv import load_dotenv

def handle_setup_env():
    default_port_neo4j = "7687"
    default_host_neo4j = "bolt://localhost"

    env_path = Path(__file__).resolve().parent / ".env"

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        overwrite = input("Environment file already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            exit(0)

    new_env_values = {}

    def prompt_env_var(var_name, prompt_text, default=None, optional=False):
        existing = os.getenv(var_name)
        current_default = existing or default
        prompt = f"{prompt_text} [{current_default}]: "
        value = input(prompt).strip()

        final_value = value or existing or default

        if optional and (not final_value or final_value.lower() == "none"):
            return 
        
        new_env_values[var_name] = final_value

    prompt_env_var("DB_USER", "Neo4j username", default="neo4j")
    prompt_env_var("DB_PASS", "Neo4j password", default="password")
    prompt_env_var("DB_HOST", "Neo4j host address", default=default_host_neo4j)
    prompt_env_var("DB_PORT", "Neo4j port number", default=default_port_neo4j)
    prompt_env_var("GA_TAG_ID", "Google Analytics tag ID (optional)", default="None", optional=True)

    with open(env_path, "w") as f:
        for k, v in new_env_values.items():
            f.write(f"{k}={v}\n")

    print(f"Environment file written to {env_path}")
