import argparse
import logging

from dvc.cli.command import CmdBase
from dvc.cli.utils import append_doc_link
from dvc.exceptions import DvcException
from dvc.ui import ui

logger = logging.getLogger(__name__)


class CmdExperimentsSave(CmdBase):
    def run(self):

        try:
            ref = self.repo.experiments.save(
                name=self.args.name, force=self.args.force
            )
        except DvcException:
            logger.exception("failed to save experiment")
            return 1

        if self.args.json:
            ui.write_json({"ref": ref})
            # fixme: add metrics
        else:
            name = self.repo.experiments.get_exact_name(ref)
            ui.write(f"Experiment has been saved as: {name}")
            ui.write(
                "\nTo promote an experiment to a Git branch run:\n\n"
                "\tdvc exp branch <exp> <branch>\n"
            )
            if self.args.metrics:
                from dvc.compare import show_metrics

                metrics = self.repo.metrics.show(revs=(ref,))
                metrics.pop("workspace", None)
                show_metrics(metrics)

        return 0


def add_parser(experiments_subparsers, parent_parser):
    EXPERIMENTS_SAVE_HELP = "Save current workspace as a dvc experiment."
    save_parser = experiments_subparsers.add_parser(
        "save",
        parents=[parent_parser],
        description=append_doc_link(EXPERIMENTS_SAVE_HELP, "exp/save"),
        help=EXPERIMENTS_SAVE_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    save_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="Save even if hash value for dependencies/outputs changed.",
    )
    save_parser.add_argument(
        "--json",
        "--show-json",
        action="store_true",
        default=False,
        help="Show output in JSON format.",
    )
    save_parser.add_argument(
        "-m",
        "--metrics",
        action="store_true",
        default=False,
        help="Show metrics for the saved experiment.",
    )
    save_parser.add_argument(
        "-n",
        "--name",
        default=None,
        help=(
            "Human-readable experiment name. If not specified, a name will "
            "be auto-generated."
        ),
        metavar="<name>",
    )
    save_parser.set_defaults(func=CmdExperimentsSave)