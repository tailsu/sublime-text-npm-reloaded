import sublime
import sublime_plugin
import subprocess
import re


ID = 'c24f5128ec3046d8ad5b7f804d23bf26'


class ViewPrintC24f5128ec3046d8ad5b7f804d23bf26Command(sublime_plugin.TextCommand):
    def run(self, edit, line):
        self.view.insert(edit, self.view.size(), line)


class ShellExecuteC24f5128ec3046d8ad5b7f804d23bf26Command(sublime_plugin.WindowCommand):
    def __init__(self, window):
        sublime_plugin.WindowCommand.__init__(self, window)
        self.process = None
        self.panel = None
        self.command = None
        self.command_args = None
        self.input_args = None
        self.waiting_for = None

    def run(self, command, **kwargs):
        folders = self.window.folders()
        if len(folders) == 0:
            sublime.error_message('Open a folder to serve as the current working directory.')
            return

        self.command = command
        self.command_args = kwargs
        self.input_args = None
        self._execute_or_input()

    def _execute_or_input(self):
        if self.command_args is not None and len(self.command_args) > 0:
            arg = next(iter(self.command_args))
            self.waiting_for = arg
            self.window.show_input_panel(self.command_args[arg], '', self._process_input, None, None)
            return

        self.panel = self.window.find_output_panel(ID) or self.window.create_output_panel(ID)
        self.panel.set_scratch(True)
        self.panel.run_command("select_all")
        self.panel.run_command("right_delete")

        self.window.run_command('show_panel', { 'panel': 'output.' + ID })

        if self.input_args is not None:
            for arg, value in self.input_args.items():
                self.command = re.sub('\$' + arg, value, self.command)

        self.panel.run_command('view_print_c24f5128ec3046d8ad5b7f804d23bf26', {'line': "$ " + self.command +  "\n\n"})
        self.process = subprocess.Popen(self.command,
            shell=True,
            cwd=self.window.folders()[0],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        sublime.set_timeout_async(self._readlines, 5)

    def _process_input(self, input):
        if self.input_args is None:
            self.input_args = dict()
        self.input_args[self.waiting_for] = input
        del self.command_args[self.waiting_for]
        self._execute_or_input()

    def _readlines(self):
        while True:
            nextline = self.process.stdout.readline().decode('utf-8')

            if nextline:
                self.panel.run_command('view_print_c24f5128ec3046d8ad5b7f804d23bf26', {'line': nextline})
            else:
                if self.process.poll() != None:
                    self.panel.run_command('view_print_c24f5128ec3046d8ad5b7f804d23bf26', {'line': '\n\n--------------------\nnpm command complete\n'})
                    self.window.status_message('npm command complete')
                    return

                sublime.set_timeout_async(self._readlines, 5)
                break;


