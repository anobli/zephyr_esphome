import pb_crpc

from pathlib import Path
from west.commands import WestCommand

class CRPCWestCommand(WestCommand):

    def __init__(self):
        super().__init__(
            'pb-crpc',
            'Generate RPC and useful functions from protobuf files',
            ''
        )

    def do_add_parser(self, parser_adder):
        parser = parser_adder.add_parser(self.name,
                                         help=self.help,
                                         description=self.description)
        return parser

    def do_run(self, args, unknown_args):
        src_dir = Path(__file__).resolve().parent.parent
        rpc_dir = src_dir / 'subsys/net/lib/esphome/components/api/rpc/'

        module_lib_dir = src_dir.parent / "modules/lib"
        esphome_inc_dir = module_lib_dir / "esphome/esphome/components/api/"

        zephyr_dir = src_dir.parent / "zephyr"
        clang_format_style = zephyr_dir / ".clang-format"

        parser = pb_crpc.setup_parser()
        pb_crpc_args = parser.parse_args([
            '--platform', 'zephyr',
            '--project', 'esphome',
            '-O', str(rpc_dir),
            '-I', str(esphome_inc_dir),
            'api.proto'
        ])
        src_dir = Path(__file__).resolve().parent.parent
        tpl_dir = src_dir / "templates"
        pb_crpc.generate(pb_crpc_args, tpl_dir, str(clang_format_style))
