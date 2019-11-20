#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os 
import sys
import hashlib
import subprocess as sp
import panflute as pf
from time import monotonic as timer
from shutil import which

MERMAID_BIN = os.path.expanduser(os.environ.get('MERMAID_BIN', 'mmdc'))
PUPPETEER_CFG = os.path.expanduser(os.environ.get('PUPPETEER_CFG', None))

class MermaidInline(object):
    """
    Converts Link inmermaid class to Image
    requires `mmdc` in PATH
    option can be provided as attributes or can set default values in yaml metadata block

    option          | metadata              | default
    ----------------|-----------------------|----------
    font-family     | svgbob.font-family    | "Arial"
    font-size       | svgbob.font-size      | 14
    scale           | svgbob.scale          | 1
    stroke_width    | svgbob.stroke-width   | 2

    """
    def __init__(self):
        self.dir_to = "svg"
        assert which("mmdc"), "mmdc is not in path"

    def action(self, elem, doc):
        if isinstance(elem, pf.Link) and "mermaid" in elem.classes:
            fn = elem.url
            options = elem.attributes
            caption = elem.content

            meta_theme = doc.get_metadata("mermaid.theme", "default")
            meta_background_color = doc.get_metadata("mermaid.background-color", "white")
            meta_css = doc.get_metadata("mermaid.css", "")

            theme = options.get("theme", meta_theme)
            background_color = options.get("background-color", meta_background_color)
            css = options.get("css", meta_css)

            mermaid_option = " ".join([
                "--theme {}".format(theme) if theme is not None else "",
                "--backgroundColor {}".format(background_color) if background_color is not None else "",
                "--puppeteerConfigFile {}".format(PUPPETEER_CFG) if PUPPETEER_CFG is not None else ""
                #"--cssFile {}".format(css) if css is not None else ""
            ])

            if not os.path.exists(self.dir_to):
                os.mkdir(self.dir_to)

            data = open(fn, "r", encoding="utf-8").read()
            counter = hashlib.sha1(data.encode("utf-8")).hexdigest()[:8]
            self.basename = "/".join([self.dir_to, str(counter)])

            _format = "svg"

            fn = os.path.abspath(fn)
            linkto = os.path.abspath(".".join([self.basename, _format])).replace("\\", "/")

            command = "{} -i {} {} -o {}".format(MERMAID_BIN, fn, mermaid_option, linkto)
            start = timer()
            pf.debug(command)
            #with sp.Popen(command, shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE) as process:
            with sp.Popen(command, shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE) as process:
                try:
                    output = process.communicate(timeout=1)[0]
                except TimeoutExpired:
                    os.killpg(process.pid, signal.SIGINT)
                    output = process.communicate()[0]
            pf.debug('Elapsed: {:.2f}'.format(timer() - start))
            pf.debug(output)
            #output = sp.check_output(command, shell=True)
            #print(output)
            #exit_codes = p1.wait()
            #(output, err) = p1.communicate()
            #print(output)

            pf.debug("[inline] generate mermaid from {} to {}".format(fn, linkto))
            elem.classes.remove("mermaid")
            elem = pf.Image(*caption, classes=elem.classes, url=linkto,
                            identifier=elem.identifier, title="fig:", attributes=elem.attributes)
            return elem

def main(doc=None):
    mi = MermaidInline()
    pf.run_filters([mi.action], doc=doc)
    return doc

if __name__ == "__main__":
    main()
