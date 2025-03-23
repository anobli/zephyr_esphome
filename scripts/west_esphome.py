import os
from pathlib import Path
from west.commands import WestCommand  # your extension must subclass this
from esphome_transpiler.esphome import generate_dts_bindings, get_project_path, generate_app

class ESPHomeWestCommand(WestCommand):

    def __init__(self):
        super().__init__(
            'esphome',
            'utility command to build and flash ESPHome device',
            ''
        )

    def do_add_parser(self, parser_adder):
        parser = parser_adder.add_parser(self.name,
                                         help=self.help,
                                         description=self.description)
        sub_parser = parser.add_subparsers(dest="subcommand")

        compile_parser = sub_parser.add_parser("compile")
        compile_parser.add_argument('yaml', help='Yaml to use to configure ESPHome')

        bindings_parser = sub_parser.add_parser("dts_bindings")

        return parser

    def do_run(self, args, unknown_args):
        current_dir = Path(os.getcwd())
        esphome_dir = Path(__file__).parent.parent
        dts_bindings_dir = esphome_dir / "dts/bindings/misc/esphome"
        if args.subcommand == "dts_bindings":
            generate_dts_bindings(dts_bindings_dir)

        if args.subcommand == "compile":
            project_path = get_project_path(args.yaml, current_dir)
            generate_app(args.yaml, project_path)
#            west(['build', str(project_path), '-p', '-d', str(project_path / 'build')])
