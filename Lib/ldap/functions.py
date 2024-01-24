"""
functions.py - wraps functions of module _ldap

See https://www.python-ldap.org/ for details.
"""

from ldap import __version__

__all__ = [
  'open','initialize','init',
  'explode_dn','explode_rdn',
  'get_option','set_option',
  'escape_str',
  'strf_secs','strp_secs',
]

import sys,pprint,time,_ldap,ldap
from calendar import timegm

from ldap import LDAPError

from ldap.dn import explode_dn,explode_rdn

from ldap.ldapobject import LDAPObject

if __debug__:
  # Tracing is only supported in debugging mode
  import traceback


def _ldap_function_call(lock,func,*args,**kwargs):
  """
  Функция-обертка, которая блокирует и регистрирует вызовы функции.

  lock
      Экземпляр threading.Lock или совместимый
  func
      Функция для вызова с переданными аргументами через *args и **kwargs
  """
  if lock:
    lock.acquire()
  if __debug__:
    if ldap._trace_level>=1:
      ldap._trace_file.write('*** {}.{} {}\n'.format(
        '_ldap',func.__name__,
        pprint.pformat((args,kwargs))
      ))
      if ldap._trace_level>=9:
        traceback.print_stack(limit=ldap._trace_stack_limit,file=ldap._trace_file)
  try:
    try:
      result = func(*args,**kwargs)
    finally:
      if lock:
        lock.release()
  except LDAPError as e:
    if __debug__ and ldap._trace_level>=2:
      ldap._trace_file.write('=> LDAPError: %s\n' % (str(e)))
    raise
  if __debug__ and ldap._trace_level>=2:
    ldap._trace_file.write('=> result:\n%s\n' % (pprint.pformat(result)))
  return result


def initialize(
    uri, trace_level=0, trace_file=sys.stdout, trace_stack_limit=None,
    bytes_mode=None, fileno=None, **kwargs
):
  """
  Возвращает экземпляр LDAPObject, открыв соединение LDAP с хостом LDAP,
  указанным URL-адресом LDAP.

  Параметры:
  uri
        URL-адрес LDAP, содержащий как минимум схему подключения и порт хоста,
        например, ldap://localhost:389
  trace_level
        Если значение не равно 0, генерируется вывод трассировки вызовов LDAP.
  trace_file
        Объект файла, в который записываются выходные данные трассировки.
        По умолчанию используется stdout.
  bytes_mode
        Следует ли включать :ref:`bytes_mode` для обратной совместимости под Py2.
  fileno
        Если значение не None, дескриптор файла сокета используется
        для подключения к серверу LDAP.

  Дополнительные ключевые аргументы (такие как ``bytes_strictness``)
  передаются в ``LDAPObject``.
  """
  return LDAPObject(
      uri, trace_level, trace_file, trace_stack_limit, bytes_mode,
      fileno=fileno, **kwargs
  )


def get_option(option):
  """
  get_option(name) -> value

  Get the value of an LDAP global option.
  """
  return _ldap_function_call(None,_ldap.get_option,option)


def set_option(option,invalue):
  """
  set_option(name, value)

  Установите значение глобальной опции LDAP.
  """
  return _ldap_function_call(None,_ldap.set_option,option,invalue)


def escape_str(escape_func,s,*args):
  """
  Applies escape_func() to all items of `args' and returns a string based
  on format string `s'.
  """
  return s % tuple(escape_func(v) for v in args)


def strf_secs(secs):
    """
    Convert seconds since epoch to a string compliant to LDAP syntax GeneralizedTime
    """
    return time.strftime('%Y%m%d%H%M%SZ', time.gmtime(secs))


def strp_secs(dt_str):
    """
    Convert LDAP syntax GeneralizedTime to seconds since epoch
    """
    return timegm(time.strptime(dt_str, '%Y%m%d%H%M%SZ'))
