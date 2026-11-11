"""`python -m recruit_cli` runs the same command line as `recruit-cli`."""

from recruit_cli.main import app

app(prog_name="recruit-cli")
