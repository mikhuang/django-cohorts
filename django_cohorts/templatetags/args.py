# http://www.sprklab.com/notes/13-passing-arguments-to-functions-in-django-template
"""
And now we can pass the arguments to getPrice by writing {{ meeting|args:user|call:"getPrice" }}. So we set the arguments using "args" and then call the function using "call".
To call multiple arguments do {{ meeting|args:arg1|args:arg2|call:"getPrice" }}.

"""

from django import template


register = template.Library()


def callMethod(obj, methodName):
  method = getattr(obj, methodName)

  if hasattr(obj, "__callArg"):
    ret = method(*obj.__callArg)
    del obj.__callArg
    return ret
  return method()


def args(obj, arg):
  if not hasattr(obj, "__callArg"):
    obj.__callArg = []

  obj.__callArg += [arg]
  return obj


register.filter("call", callMethod)
register.filter("args", args)
