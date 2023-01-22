# Nettopp Auth API

NB: This project is still in early development.

The Nettopp Auth API is the backend server for the Nettopp Auth system.

## Deployment

### Environment variables

| Name                        | Description                                   | Default             |
| --------------------------- | --------------------------------------------- | ------------------- |
| `AUTH_DB_CONNECTION_STRING` | The connection string for the database.       | `sqlite:///auth.db` |
| `HOST`                      | The host to bind to.                          |                     |
| `JWT_PRIVATE_KEY`           | The private JWT key.                          |                     |
| `JWT_PUBLIC_KEY`            | The public JWT key.                           |                     |
| `JWT_ALGORITHM`             | The JWT algorithm to use.                     | `ES512`             |
| `PORT`                      | The port to bind to.                          |                     |
| `RELOAD`                    | Whether to reload the server on code changes. | `False`             |
| `VERBOSE`                   | Whether to print verbose logs.                | `False`             |


### Key generation
```bash
openssl ecparam -name secp521r1 -genkey -noout -out private.pem
openssl ec -in private.pem -pubout -out public.pem
```

Ref: https://notes.salrahman.com/generate-es256-es384-es512-private-keys/

### Deployment on a host machine
```bash
# Here's the deployment workflow for Debian-based systems.
# Run the appropriate commands for your target system.

# Set up a virtual environment.
python -m venv venv

# Activate the virtual environment.
source venv/bin/activate

# Install the dependencies.
python -m pip install -e .

# Run the code
TODO: Add instructions.
```

### Deployment with Docker

TODO: Add instructions.

## Development

```bash
# Here's the workflow for Debian-based systems.
# Run the apropriate commands for your target system.

# Initialize the project for using git flow.
sudo apt install git-flow
git flow init

# Set up a virtual environment.
python -m venv venv

# Activate the virtual environment.
source venv/bin/activate

# Install the dependencies.
python -m pip install -e .[dev]

# Set up pre-commit.
pre-commit install

# Run the code.
TODO: Add instructions.
```

## Usage

TODO: Fill me in.

## Testing

TODO: Fill me in.
