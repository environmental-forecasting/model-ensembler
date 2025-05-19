import asyncio
import logging
import os
import shlex
import shutil

import jinja2

from model_ensembler.exceptions import TemplatingError
from model_ensembler.utils import Arguments


async def prepare_run_directory(batch, run):
    """ Preparing directory for each run from batch templates

    Args:
        batch (object): Whole batch configuration.
        run (object): Specific run configuration.

    Raises:
        TemplatingError: If template directory cannot be moved from source
                        to destination.
    """
    args = Arguments()

    if args.pickup and os.path.exists(run.dir):
        logging.info("Picked up previous job directory for run {}".
                     format(run.id))

        for tmpl_file in batch.templates:
            src_path = os.path.join(batch.templatedir, tmpl_file)
            dst_path = shutil.copy(src_path, os.path.join(run.dir, tmpl_file))
            logging.info("Re-copied {} to {} for template regeneration".
                         format(src_path, dst_path))
    else:
        if os.path.exists(run.dir):
            raise TemplatingError("Run directory {} already exists".
                                  format(run.dir))

        os.makedirs(run.dir, mode=0o775)

        cmd = "rsync -aXE {}/ {}/".format(batch.templatedir, run.dir)
        logging.info(cmd)
        proc = await asyncio.create_subprocess_exec(*shlex.split(cmd))
        rc = await proc.wait()

        if rc != 0:
            raise TemplatingError("Could not grab template directory {} to {}".
                                  format(batch.templatedir, run.dir))


def process_templates(run, template_list):
    """Render templates based on provided context.

    Args:
        run (object): Specific run configuration.
        template_list (list): Paths to template sources.

    Raises:
        TemplatingError: If cannot template using the provided format.
    """
    for tmpl_file in template_list:
        if tmpl_file[-3:] != ".j2":
            raise TemplatingError("{} doe not appear to be a Jinja2 template "
                                  "(.j2)".format(tmpl_file))

        try:
            tmpl_path = os.path.join(run.dir, tmpl_file)
            with open(tmpl_path, "r") as fh:
                tmpl_data = fh.read()

            dst_file = tmpl_path[:-3]
            logging.info("Templating {} to {}".format(tmpl_path, dst_file))
            tmpl = jinja2.Template(tmpl_data)
            dst_data = tmpl.render(run=run)
            with open(dst_file, "w+") as fh:
                fh.write(dst_data)
            os.chmod(dst_file, os.stat(tmpl_path).st_mode)
            os.unlink(tmpl_path)
        except OSError:
            raise TemplatingError("Could not template {}".format(tmpl_file))
