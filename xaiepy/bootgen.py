from ._bootgen import *
from textwrap import dedent


def emit_design_bif(cdo_files):
    cdo_files = "\n".join(map(lambda c: f"file={c}", cdo_files))
    return dedent(
        f"""\
        all:
        {{
          id_code = 0x14ca8093
          extended_id_code = 0x01
          image
          {{
            name=aie_image, id=0x1c000000
            {{ type=cdo
               {cdo_files}
            }}
          }}
        }}
        """
    )
