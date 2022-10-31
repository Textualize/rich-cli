import click
from click import Command
from click.decorators import FC, Parameter
from click.testing import CliRunner


class DuplicateOptionsError(ValueError):
    pass


def test_duplicate_option_flags_raises_exception(monkeypatch):
    """Create a test that will monkeypatch the click.option decorators
    so that they fail noisily when options are duplicated for a command
    """

    def _param_memo_safe(f: FC, param: Parameter) -> None:
        if isinstance(f, Command):
            f.params.append(param)
        else:
            if not hasattr(f, "__click_params__"):
                f.__click_params__ = []  # type: ignore
            else:
                for opt in param.opts:
                    for preexisting_param in f.__click_params__:
                        if opt in preexisting_param.opts:
                            raise DuplicateOptionsError(
                                "Duplicate option added to command."
                                + " The following option appears more than once:\n"
                                + f"{opt} (used for {param.human_readable_name}"
                                + f" and {preexisting_param.human_readable_name})"
                            )

            f.__click_params__.append(param)  # type: ignore

    monkeypatch.setattr(click.decorators, "_param_memo", _param_memo_safe)

    # import here (after monkeypatch) because decorators are run on import
    from rich_cli.__main__ import main

    runner = CliRunner()
    runner.invoke(main)
