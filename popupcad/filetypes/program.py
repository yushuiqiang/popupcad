# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import sys
import PySide.QtGui as qg
import popupcad
import logging

class Program(object):

    def __init__(self, plugins, *args, **kwargs):

        args = list(args)

        for item in args:
            if '--deprecated' in item:
                import popupcad_deprecated
                popupcad.deprecated = popupcad_deprecated
                sys.modules['popupcad.deprecated'] = popupcad_deprecated
                args.pop(args.index(item))

        self.app = qg.QApplication(args[0])
        self.app.setWindowIcon(popupcad.supportfiles.Icon('popupcad'))
        self.editor = popupcad.guis.editor.Editor()

        if len(args) > 1 and not '--' in args[-1]:
            self.editor.open(filename=args[-1])
        self.editor.show()
        for plugin in plugins:
            plugin.initialize(self)
        self.create_exception_listener()
    def create_exception_listener(self):
        logging.basicConfig(filename='log.txt',filemode='w',level=logging.DEBUG)
        import sys
        self.excepthook_internal = sys.excepthook
        sys.excepthook = self.excepthook
    def excepthook(self,exctype,value,traceback):
        message = \
'''
Exception: {}
Value: {}
Traceback: {}
'''.format(str(exctype),str(value),str(traceback))
        print(message)
        logging.error(message)
        self.editor.error_log.appendText(message)
        self.excepthook_internal(exctype,value,traceback)
        mb = qg.QMessageBox()
        mb.setText(message)
        mb.exec_()
        
        
