window = None


def Exit(exitCode, reason="No exit reason provided"):
    window.close()
    exit(exitCode)
