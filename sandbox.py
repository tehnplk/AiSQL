def read_db_config():
    config = {}

    with open("sandbox.txt", "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key] = value

    return {
        "MYSQL_HOST": config.get("HOST"),
        "MYSQL_PORT": config.get("PORT"),
        "MYSQL_USER": config.get("USER"),
        "MYSQL_PASSWORD": config.get("PASSWORD"),
        "MYSQL_DATABASE": config.get("DATABASE"),
    }
