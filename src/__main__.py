"""Entry point for the OpenProject TUI application."""

from .app import OpenProjectApp


def main():
    """Run the OpenProject TUI application."""
    app = OpenProjectApp()
    app.run()


if __name__ == "__main__":
    main()
