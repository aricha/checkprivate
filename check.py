#! /usr/bin/env python

import sys, os

def find_prefix(l, p):
    for i, v in enumerate(l):
        if v.find(p) == 0:
            return i
    return -1

def process_method(m):
    orig_method = m

    m = m.strip()
    if m.find('//') != -1:
        m = m[:m.find('//')]
    m = m.strip()

    q = '-'
    if m.find('-') != -1:
        m = m[m.find('-') + 1:]
        q = '-'
    if m.find('+') != -1:
        m = m[m.find('+') + 1:]
        q = '+'
    m = m.strip()

    paren_count = 0
    paren_start = -1
    ranges_to_delete = []
    for i, c in enumerate(m):
        if c == '(':
            if paren_count == 0: paren_start = i
            paren_count += 1
        elif c == ')': 
            paren_count -= 1
            if paren_count < 0:
                print "Malforrmed method:", orig_method
                start = i - 5 if i >= 5 else i
                end = i + 5 if len(m) < i + 5 else len(m) - i - 1
                print "Mismatched parentheses at index", i, "...{0}...".format(m[start : end])
                return ''
            elif paren_count == 0:
                is_retval = (paren_start == 0)
                n = 1 if i + 1 < len(m) and m[i + 1] == ' ' else 0
                arg_start = (i + n + 1)
                m_remainder = m[arg_start:]

                if is_retval:
                     arg_len = 0
                else: 
                    arg_len = m_remainder.find(' ') if ' ' in m_remainder else len(m_remainder)

                r = (paren_start, arg_start + arg_len)
                ranges_to_delete.append(r)

    # handle varargs
    if len(ranges_to_delete) > 1:
        lstart, lend = ranges_to_delete[-1]
        if lend < len(m) - 2:
            ranges_to_delete[-1] = (lstart, len(m) - 1)

    for start, end in reversed(ranges_to_delete):
        m = m[:start] + m[end:]
    
    if len(m) > 0 and m[len(m) - 1] == ';':
        m = m[:-1]
    m = m.strip()

    m = m.replace(' ', '')
    m = q + m

    return m

def process_property(p):
    p = p.strip()
    if p.find('//') != -1:
        p = p[:p.find('//')]
    p = p.strip()

    p = p[len('@property'):]
    p = p.strip()

    attrs = ['readwrite']
    if p[0] == '(':
        attrs = p[1:p.find(')')].split(',')
        attrs = [a.strip() for a in attrs]

        p = p[p.find(')') + 1:]
        p.strip()
   
    if p[len(p) - 1] == ';':
        p = p[:-1]
    p = p.strip()

    name = p[max(p.rfind(' '), p.rfind('*'), p.rfind(']')) + 1:].strip()
   
    getter = name
    if find_prefix(attrs, 'getter') != -1:
        getter = attrs[find_prefix(attrs, 'getter')]
        getter = getter[getter.find('=') + 1:].strip()
    methods = [getter]
    
    if find_prefix(attrs, 'readonly') == -1:
        setter = 'set%s:' % (name[0].capitalize() + name[1:])
        if find_prefix(attrs, 'setter') != -1:
            setter = attrs[find_prefix(attrs, 'setter')]
            setter = setter[setter.find('=') + 1:].strip()
        methods.append(setter)

    methods = ['-'+m for m in methods]
    return methods

def find_methods(header):
    header = header.split('\n')
    out = {}

    while find_prefix(header, '@interface') != -1:
        cls = header[find_prefix(header, '@interface')]
        cls = cls[len('@interface '):cls.find(' : ')] if ' : ' in cls else (cls[len('@interface '):cls.find('(')] if '(' in cls else cls[len('@interface '):])
        cls = cls.strip()

        header = header[find_prefix(header, '@interface') + 1:]
        working = header[:find_prefix(header, '@end')]

        methods = []
        for m in working:
            s = m.strip()
            if s.find('^') != -1:
                continue
            elif s.find('-') == 0 or s.find('+') == 0:
                methods.append(process_method(m))
            elif s.find('@property') == 0:
                methods = methods + process_property(m)

        out[cls] = methods

    return out

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: %s iPhonePrivate.h SpringBoard/" % sys.argv[0]
        sys.exit(0)

    header = open(sys.argv[1], 'r').read()
    header_methods = find_methods(header)

    missing_header_methods = header_methods.copy()
    missing_header_classes = header_methods.keys()

    def parse_file(f):
        class_methods = find_methods(f)
        for c in missing_header_methods:
            if c in class_methods:
                cv = class_methods[c] 
                hv = missing_header_methods[c] 
                missing_header_methods[c] = [x for x in hv if x not in cv]
                if c in missing_header_classes: missing_header_classes.remove(c)

    class_root = sys.argv[2]
    if os.path.isdir(class_root):
        print "Searching for headers..."
        for root, dirs, files in os.walk(class_root):
            for fname in files:
                with open(os.path.join(root, fname), 'r') as f:
                    lines = [line for line in f]
                parse_file(''.join(lines))
    else:
        parse_file(open(class_root, 'r').read())

    # ignore missing methods for missing classes
    for c in missing_header_classes: del missing_header_methods[c]
    method_count = sum(len(ml) for ml in missing_header_methods.itervalues())

    print "Found %d missing classes, %d missing methods" % (len(missing_header_classes), method_count)
    for c in sorted(missing_header_classes, key=str.lower):
        print "Missing class: %s" % c
    for c in sorted(missing_header_methods, key=str.lower):
        for m in sorted(missing_header_methods[c], key=str.lower):
            print "%s: %s" % (c, m)


