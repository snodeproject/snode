import argparse
import json
import os
import io
import contextlib
import posixpath
import re
import sys
import urllib.error
import urllib.request
import helpers.remove as remover

remover.ignore_initial_userwarning()

REPO_BASE = "https://raw.githubusercontent.com/snodeproject/spmrc/main"
REQUIRE_RE = re.compile(r"require\s*\(\s*(['\"])([^'\"]+)\1\s*\)")


@contextlib.contextmanager
def suppress_stderr():
    """Temporarily suppress stderr and stdout output."""
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    sys.stderr = io.StringIO()
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stderr = old_stderr
        sys.stdout = old_stdout


try:
    from py_mini_racer import py_mini_racer
except ImportError:
    py_mini_racer = None


def normalize_module_id(path):
    path = path.replace('\\', '/')
    return posixpath.normpath(path)


def fs_path(module_id):
    return os.path.normpath(module_id.replace('/', os.sep))


def find_require_strings(source):
    return [match.group(2) for match in REQUIRE_RE.finditer(source)]


def file_exists(module_id):
    return os.path.isfile(fs_path(module_id))


def add_js_extension(module_id):
    if module_id.endswith('.js'):
        return module_id
    return module_id + '.js'


def resolve_package_module(name, from_dir, cwd):
    candidate = normalize_module_id(posixpath.join(from_dir, 'snode_modules', name, 'main.js'))
    if file_exists(candidate):
        return candidate
    candidate = normalize_module_id(posixpath.join(cwd, 'snode_modules', name, 'main.js'))
    if file_exists(candidate):
        return candidate
    raise FileNotFoundError(
        f"Pacchetto '{name}' non trovato in {from_dir}/snode_modules o {cwd}/snode_modules"
    )


def resolve_module_name(name, from_dir, cwd):
    if name.startswith('/') or name.startswith('./') or name.startswith('../'):
        requested = normalize_module_id(posixpath.join(from_dir, name))
        if file_exists(requested):
            return requested
        requested_js = add_js_extension(requested)
        if file_exists(requested_js):
            return requested_js
        raise FileNotFoundError(f"Impossibile trovare '{name}' da {from_dir}")

    if os.name == 'nt' and re.match(r'^[A-Za-z]:', name):
        requested = normalize_module_id(name)
        if file_exists(requested):
            return requested
        requested_js = add_js_extension(requested)
        if file_exists(requested_js):
            return requested_js
        raise FileNotFoundError(f"Impossibile trovare '{name}'")

    return resolve_package_module(name, from_dir, cwd)


class ModuleGraph:
    def __init__(self, cwd):
        self.cwd = normalize_module_id(cwd)
        self.sources = {}
        self.require_maps = {}
        self.loaded = set()
        self.registered = set()

    def load_module(self, module_id):
        module_id = normalize_module_id(module_id)
        if module_id in self.loaded:
            return
        path = fs_path(module_id)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File modulo non trovato: {module_id}")
        with open(path, 'r', encoding='utf-8') as handle:
            source = handle.read()
        self.sources[module_id] = source
        self.loaded.add(module_id)
        self.require_maps[module_id] = {}
        parent_dir = posixpath.dirname(module_id)
        for dependency in find_require_strings(source):
            resolved = resolve_module_name(dependency, parent_dir, self.cwd)
            self.require_maps[module_id][dependency] = resolved
            self.load_module(resolved)

    def new_module_ids(self):
        return [module_id for module_id in self.sources if module_id not in self.registered]

    def module_definition(self, module_id):
        require_map = json.dumps(self.require_maps.get(module_id, {}))
        source = self.sources[module_id]
        return (
            f"__module_require_map[{json.dumps(module_id)}] = {require_map};\n"
            f"__module_registry[{json.dumps(module_id)}] = function(exports, module, __filename, __dirname, require) {{\n"
            f"{source}\n"
            f"}};\n"
        )


def build_prelude():
    return """
var __module_registry = {};
var __module_cache = {};
var __module_require_map = {};
var __console_messages = [];
var console = {
  log: function() {
    var args = Array.prototype.slice.call(arguments);
    __console_messages.push(args.map(function(x) {
      if (x === undefined) return 'undefined';
      if (x === null) return 'null';
      try { return x.toString(); } catch (e) { return String(x); }
    }).join(' '));
  }
};
function __drainConsole() {
  var messages = __console_messages;
  __console_messages = [];
  return messages;
}
function __normalizePath(path) {
  path = String(path).replace(/\\\\/g, '/');
  var parts = path.split('/');
  var out = [];
  for (var i = 0; i < parts.length; i++) {
    var part = parts[i];
    if (!part || part === '.') continue;
    if (part === '..') {
      if (out.length && out[out.length - 1] !== '..') {
        out.pop();
      } else {
        out.push('..');
      }
      continue;
    }
    out.push(part);
  }
  return out.join('/') || '.';
}
function __dirname_of(path) {
  path = __normalizePath(path);
  var i = path.lastIndexOf('/');
  if (i < 0) return '.';
  return path.slice(0, i);
}
function __resolvePath(base, relative) {
  if (relative.startsWith('/')) return __normalizePath(relative);
  return __normalizePath(base + '/' + relative);
}
function __makeRequire(moduleId, dirname) {
  return function(name) {
    var target = name;
    if (name.startsWith('./') || name.startsWith('../') || name.startsWith('/')) {
      target = __resolvePath(dirname, name);
    } else {
      var mapping = __module_require_map[moduleId] || {};
      if (mapping[name]) {
        target = mapping[name];
      } else {
        throw new Error('Cannot resolve module "' + name + '" from ' + moduleId);
      }
    }
    if (__module_cache[target]) {
      return __module_cache[target].exports;
    }
    if (!__module_registry[target]) {
      if (!target.endsWith('.js')) {
        var targetJs = target + '.js';
        if (__module_cache[targetJs]) {
          return __module_cache[targetJs].exports;
        }
        if (__module_registry[targetJs]) {
          target = targetJs;
        }
      }
    }
    if (!__module_registry[target]) {
      throw new Error('Module not found: ' + target);
    }
    var module = { exports: {} };
    __module_cache[target] = module;
    __module_registry[target](module.exports, module, target, __dirname_of(target), __makeRequire(target, __dirname_of(target)));
    return module.exports;
  };
}
var require = __makeRequire('repl', '.');
"""


class Snode:
    def __init__(self):
        self.cwd = os.getcwd()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.graph = ModuleGraph(self.cwd)
        self.ctx = None

    def ensure_runtime(self):
        if py_mini_racer is None:
            raise RuntimeError(
                'py_mini_racer è richiesto. Installalo con pip install py-mini-racer'
            )
        if self.ctx is None:
            self.ctx = py_mini_racer.MiniRacer()
            with suppress_stderr():
                self.ctx.eval(build_prelude())

    def register_new_modules(self):
        self.ensure_runtime()
        new_ids = self.graph.new_module_ids()
        for module_id in new_ids:
            definition = self.graph.module_definition(module_id)
            with suppress_stderr():
                self.ctx.eval(definition)
            self.graph.registered.add(module_id)

    def load_module(self, module_id):
        self.graph.load_module(module_id)
        self.register_new_modules()

    def run_js_file(self, script_path):
        script_path = os.path.abspath(script_path)
        if not os.path.isfile(script_path):
            if not script_path.endswith('.js'):
                candidate = script_path + '.js'
                if os.path.isfile(candidate):
                    script_path = candidate
            if not os.path.isfile(script_path):
                raise FileNotFoundError(f"Script non trovato: {script_path}")

        module_id = normalize_module_id(script_path)
        main_dir = normalize_module_id(os.path.dirname(script_path) or '.')
        try:
            self.ensure_runtime()
            self.load_module(module_id)
            run_code = (
                f"var __main_result = (function() {{ var module = {{ exports: {{}} }}; __module_cache[{json.dumps(module_id)}] = module; "
                f"__module_registry[{json.dumps(module_id)}](module.exports, module, {json.dumps(module_id)}, {json.dumps(main_dir)}, __makeRequire({json.dumps(module_id)}, {json.dumps(main_dir)})); "
                f"return module.exports; }})(); var __main_logs = __drainConsole(); var __main_result_payload = {{result: __main_result, logs: __main_logs}}; JSON.stringify(__main_result_payload);"
            )
            with suppress_stderr():
                raw = self.ctx.eval(run_code)
            payload = None
            try:
                if isinstance(raw, (bytes, bytearray)):
                    raw = raw.decode('utf-8')
                if isinstance(raw, str):
                    payload = json.loads(raw)
            except Exception:
                payload = None

            if isinstance(payload, dict):
                for line in (payload.get('logs') or []):
                    print(line)
                if payload.get('result') is not None:
                    print(payload.get('result'))
            else:
                if raw is not None:
                    print(raw)
        except Exception as exc:
            print(f"Errore durante l'esecuzione dello script: {exc}")
            return

    def install_package(self, name, global_install=False):
        url = f"{REPO_BASE}/{name}.js"
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Errore nel download di {name}: {exc.code} {exc.reason}") from exc
        base_dir = self.script_dir if global_install else self.cwd
        package_dir = os.path.join(base_dir, 'snode_modules', name)
        os.makedirs(package_dir, exist_ok=True)
        target = os.path.join(package_dir, 'main.js')
        with open(target, 'w', encoding='utf-8') as handle:
            handle.write(content)
        print(f"Installato {name} in {target}")
        return target

    def prepare_repl_input(self, source):
        for dependency in find_require_strings(source):
            if dependency.startswith('./') or dependency.startswith('../') or dependency.startswith('/') or (
                os.name == 'nt' and re.match(r'^[A-Za-z]:', dependency)
            ):
                base_dir = normalize_module_id(self.cwd)
            else:
                base_dir = normalize_module_id(self.cwd)
            try:
                resolved = resolve_module_name(dependency, base_dir, self.cwd)
            except FileNotFoundError:
                continue
            if resolved not in self.graph.loaded:
                self.load_module(resolved)

    def repl(self):
        self.ensure_runtime()
        print('Snode REPL 0.1.0 (digita exit o quit per uscire)')
        while True:
            try:
                source = input('snode> ')
            except EOFError:
                print()
                break
            if not source:
                continue
            if source.strip() in ('exit', 'quit'):
                break
            try:
                self.prepare_repl_input(source)
                code = (
                    f"var __repl_result = (function() {{ return eval({json.dumps(source)}); }})(); "
                    "var __repl_logs = __drainConsole(); var __repl_payload = {result: __repl_result, logs: __repl_logs}; JSON.stringify(__repl_payload);"
                )
                with suppress_stderr():
                    raw = self.ctx.eval(code)
                payload = None
                try:
                    if isinstance(raw, (bytes, bytearray)):
                        raw = raw.decode('utf-8')
                    if isinstance(raw, str):
                        payload = json.loads(raw)
                except Exception:
                    payload = None
                if isinstance(payload, dict):
                    for line in (payload.get('logs') or []):
                        print(line)
                    if payload.get('result') is not None:
                        print(payload.get('result'))
                else:
                    print(raw)
            except Exception as exc:
                print('Errore:', exc)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] == 'spm':
        spm_parser = argparse.ArgumentParser(
            prog='snode spm',
            description='Gestore di pacchetti Snode - Snode Package Manager'
        )
        spm_subparsers = spm_parser.add_subparsers(dest='spm_command', help='Azioni SPM')
        install_parser = spm_subparsers.add_parser('install', help='Installa un pacchetto')
        install_parser.add_argument('name', help='Nome pacchetto da installare')
        install_parser.add_argument('-g', '--global', dest='global_install', action='store_true', help='Installa globalmente il pacchetto')
        spm_args = spm_parser.parse_args(argv[1:])
        node = Snode()
        if spm_args.spm_command != 'install':
            spm_parser.print_help()
            return
        try:
            node.install_package(spm_args.name, global_install=spm_args.global_install)
        except Exception as exc:
            print(f"Errore: {exc}")
            return
        return

    parser = argparse.ArgumentParser(
        prog='snode',
        description='Snode: runtime in Python simile a Node.js con V8 e SPM'
    )
    parser.add_argument('script', nargs='?', help='File JavaScript da eseguire')
    parser.add_argument('-e', '--eval', dest='eval_expr', help='Valuta codice JavaScript ed esce')
    parser.add_argument('--version', action='store_true', help='Stampa la versione ed esce')
    args = parser.parse_args(argv)
    node = Snode()

    if args.version:
        print('Snode v0.1.0 - SPM v26.0')
        return

    if args.eval_expr:
        node.ensure_runtime()
        node.prepare_repl_input(args.eval_expr)
        code = (
            f"var __eval_result = (function() {{ return eval({json.dumps(args.eval_expr)}); }})(); "
            "var __eval_logs = __drainConsole(); var __eval_result_payload = {result: __eval_result, logs: __eval_logs}; JSON.stringify(__eval_result_payload);"
        )
        with suppress_stderr():
            raw = node.ctx.eval(code)
        payload = None
        try:
            if isinstance(raw, (bytes, bytearray)):
                raw = raw.decode('utf-8')
            if isinstance(raw, str):
                payload = json.loads(raw)
        except Exception:
            payload = None
        if isinstance(payload, dict):
            for line in (payload.get('logs') or []):
                print(line)
            if payload.get('result') is not None:
                print(payload.get('result'))
        else:
            print(raw)
        return

    if args.script:
        try:
            node.run_js_file(args.script)
        except Exception as exc:
            print(f"Errore: {exc}")
        return

    try:
        node.repl()
    except Exception as exc:
        print(f"Errore: {exc}")


if __name__ == '__main__':
    main()
