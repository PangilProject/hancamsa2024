"""
아주 작은 템플릿 엔진.

외부 의존성 없이 이 사이트에 필요한 문법만 지원한다.

    {{ value }}                 컨텍스트 값 (HTML 이스케이프)
    {{& value }}                컨텍스트 값 (원문 그대로)
    {% for item in list %} … {% endfor %}
    {% if value %} … {% else %} … {% endif %}      (not 도 사용 가능)
    {% include "_nav.html" %}

값은 점 표기로 찾는다 (item.label). 반복문 안에서는 loop.index / loop.first / loop.last 를 쓸 수 있다.
"""

import html
import os
import re

TOKEN = re.compile(r"({%.*?%}|{{.*?}})", re.S)


class Text:
    def __init__(self, s):
        self.s = s

    def render(self, ctx, env):
        return self.s


class Var:
    def __init__(self, expr, raw):
        self.expr, self.raw = expr, raw

    def render(self, ctx, env):
        v = lookup(ctx, self.expr)
        if v is None:
            return ""
        s = str(v)
        return s if self.raw else html.escape(s, quote=True)


class For:
    def __init__(self, name, expr, body):
        self.name, self.expr, self.body = name, expr, body

    def render(self, ctx, env):
        items = lookup(ctx, self.expr) or []
        out = []
        n = len(items)
        for i, item in enumerate(items):
            scope = dict(ctx)
            scope[self.name] = item
            scope["loop"] = {"index": i + 1, "index0": i, "first": i == 0, "last": i == n - 1}
            out.append(render_nodes(self.body, scope, env))
        return "".join(out)


class If:
    def __init__(self, expr, body, orelse):
        self.expr, self.body, self.orelse = expr, body, orelse

    def render(self, ctx, env):
        expr, negate = self.expr, False
        if expr.startswith("not "):
            expr, negate = expr[4:].strip(), True
        truthy = bool(lookup(ctx, expr))
        if negate:
            truthy = not truthy
        return render_nodes(self.body if truthy else self.orelse, ctx, env)


class Include:
    def __init__(self, name):
        self.name = name

    def render(self, ctx, env):
        return render_nodes(env.parse(self.name), ctx, env)


def lookup(ctx, expr):
    cur = ctx
    for part in expr.strip().split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
        if cur is None:
            return None
    return cur


def render_nodes(nodes, ctx, env):
    return "".join(n.render(ctx, env) for n in nodes)


def parse(src):
    nodes, stack = [], []

    def push(node):
        (stack[-1][1] if stack else nodes).append(node)

    for tok in TOKEN.split(src):
        if not tok:
            continue
        if tok.startswith("{{"):
            body = tok[2:-2].strip()
            raw = body.startswith("&")
            push(Var(body[1:].strip() if raw else body, raw))
        elif tok.startswith("{%"):
            stmt = tok[2:-2].strip()
            if stmt.startswith("for "):
                m = re.match(r"for\s+(\w+)\s+in\s+(\S+)$", stmt)
                if not m:
                    raise SyntaxError(f"for 구문 오류: {stmt}")
                stack.append(("for", [], m.group(1), m.group(2)))
            elif stmt == "endfor":
                kind, body, name, expr = stack.pop()
                assert kind == "for", "endfor 짝이 맞지 않습니다"
                push(For(name, expr, body))
            elif stmt.startswith("if "):
                stack.append(("if", [], stmt[3:].strip(), None))
            elif stmt == "else":
                kind, body, expr, _ = stack.pop()
                assert kind == "if", "else 는 if 안에서만 쓸 수 있습니다"
                stack.append(("else", [], expr, body))
            elif stmt == "endif":
                kind, body, expr, ifbody = stack.pop()
                push(If(expr, ifbody, body) if kind == "else" else If(expr, body, []))
            elif stmt.startswith("include "):
                push(Include(stmt.split(None, 1)[1].strip().strip('"\'')))
            else:
                raise SyntaxError(f"알 수 없는 구문: {stmt}")
        else:
            push(Text(tok))

    if stack:
        raise SyntaxError(f"닫히지 않은 블록: {stack[-1][0]}")
    return nodes


class Env:
    def __init__(self, root):
        self.root = root
        self._cache = {}

    def parse(self, name):
        if name not in self._cache:
            with open(os.path.join(self.root, name), encoding="utf-8") as f:
                self._cache[name] = parse(f.read())
        return self._cache[name]

    def render(self, name, ctx):
        return render_nodes(self.parse(name), ctx, self)
