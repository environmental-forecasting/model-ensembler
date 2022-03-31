import logging
import os

import jinja2

from model_ensembler.batcher import ctx


def process_templates(template_list):
    """Render templates based on provided context

    Args:
        ctx (object): context object for retrieving configuration
        template_list (list): list of paths to template sources
    """
    run_ctx = ctx.get()

    for tmpl_file in template_list:
        if tmpl_file[-3:] != ".j2":
            raise RuntimeError("{} doe not appear to be a Jinja2 template "
                               "(.j2)".format(tmpl_file))

        tmpl_path = os.path.join(run_ctx.dir, tmpl_file)
        with open(tmpl_path, "r") as fh:
            tmpl_data = fh.read()

        dst_file = tmpl_path[:-3]
        logging.info("Templating {} to {}".format(tmpl_path, dst_file))
        tmpl = jinja2.Template(tmpl_data)
        dst_data = tmpl.render(run=run_ctx)
        with open(dst_file, "w+") as fh:
            fh.write(dst_data)
        os.chmod(dst_file, os.stat(tmpl_path).st_mode)

        os.unlink(tmpl_path)
