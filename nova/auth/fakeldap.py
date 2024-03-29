# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Fake LDAP server for test harnesses.

This class does very little error checking, and knows nothing about ldap
class definitions. It implements the minimum emulation of the python ldap
library to work with nova.
"""

import json

from nova import datastore


SCOPE_SUBTREE  = 2
MOD_ADD = 0
MOD_DELETE = 1


class NO_SUCH_OBJECT(Exception):
    pass


class OBJECT_CLASS_VIOLATION(Exception):
    pass


def initialize(uri):
    return FakeLDAP()


def _match_query(query, attrs):
    """Match an ldap query to an attribute dictionary.

    &, |, and ! are supported in the query. No syntax checking is performed,
    so malformed querys will not work correctly.

    """
    # cut off the parentheses
    inner = query[1:-1]
    if inner.startswith('&'):
        # cut off the &
        l, r = _paren_groups(inner[1:])
        return _match_query(l, attrs) and _match_query(r, attrs)
    if inner.startswith('|'):
        # cut off the |
        l, r = _paren_groups(inner[1:])
        return _match_query(l, attrs) or _match_query(r, attrs)
    if inner.startswith('!'):
        # cut off the ! and the nested parentheses
        return not _match_query(query[2:-1], attrs)

    (k, sep, v) = inner.partition('=')
    return _match(k, v, attrs)


def _paren_groups(source):
    """Split a string into parenthesized groups."""
    count = 0
    start = 0
    result = []
    for pos in xrange(len(source)):
        if source[pos] == '(':
            if count == 0:
                start = pos
            count += 1
        if source[pos] == ')':
            count -= 1
            if count == 0:
                result.append(source[start:pos+1])
    return result


def _match(k, v, attrs):
    """Match a given key and value against an attribute list."""
    if k not in attrs:
        return False
    if k != "objectclass":
        return v in attrs[k]
    # it is an objectclass check, so check subclasses
    values = _subs(v)
    for value in values:
        if value in attrs[k]:
            return True
    return False


def _subs(value):
    """Returns a list of subclass strings.

    The strings represent the ldap objectclass plus any subclasses that
    inherit from it. Fakeldap doesn't know about the ldap object structure,
    so subclasses need to be defined manually in the dictionary below.

    """
    subs = {'groupOfNames': ['novaProject']}
    if value in subs:
        return [value] + subs[value]
    return [value]


def _from_json(encoded):
    """Convert attribute values from json representation.

    Args:
    encoded -- a json encoded string

    Returns a list of strings

    """
    return [str(x) for x in json.loads(encoded)]


def _to_json(unencoded):
    """Convert attribute values into json representation.

    Args:
    unencoded -- an unencoded string or list of strings.  If it
        is a single string, it will be converted into a list.

    Returns a json string

    """
    return json.dumps(list(unencoded))


class FakeLDAP(object):
    #TODO(vish): refactor this class to use a wrapper instead of accessing
    #            redis directly

    def simple_bind_s(self, dn, password):
        """This method is ignored, but provided for compatibility."""
        pass

    def unbind_s(self):
        """This method is ignored, but provided for compatibility."""
        pass

    def add_s(self, dn, attr):
        """Add an object with the specified attributes at dn."""
        key = "%s%s" % (self.__redis_prefix, dn)

        value_dict = dict([(k, _to_json(v)) for k, v in attr])
        datastore.Redis.instance().hmset(key, value_dict)

    def delete_s(self, dn):
        """Remove the ldap object at specified dn."""
        datastore.Redis.instance().delete("%s%s" % (self.__redis_prefix, dn))

    def modify_s(self, dn, attrs):
        """Modify the object at dn using the attribute list.

        Args:
        dn -- a dn
        attrs -- a list of tuples in the following form:
            ([MOD_ADD | MOD_DELETE], attribute, value)

        """
        redis = datastore.Redis.instance()
        key = "%s%s" % (self.__redis_prefix, dn)

        for cmd, k, v in attrs:
            values = _from_json(redis.hget(key, k))
            if cmd == MOD_ADD:
                values.append(v)
            else:
                values.remove(v)
            values = redis.hset(key, k, _to_json(values))

    def search_s(self, dn, scope, query=None, fields=None):
        """Search for all matching objects under dn using the query.

        Args:
        dn -- dn to search under
        scope -- only SCOPE_SUBTREE is supported
        query -- query to filter objects by
        fields -- fields to return. Returns all fields if not specified

        """
        if scope != SCOPE_SUBTREE:
            raise NotImplementedError(str(scope))
        redis = datastore.Redis.instance()
        keys = redis.keys("%s*%s" % (self.__redis_prefix, dn))
        objects = []
        for key in keys:
            # get the attributes from redis
            attrs = redis.hgetall(key)
            # turn the values from redis into lists
            attrs = dict([(k, _from_json(v))
                          for k, v in attrs.iteritems()])
            # filter the objects by query
            if not query or _match_query(query, attrs):
                # filter the attributes by fields
                attrs = dict([(k, v) for k, v in attrs.iteritems()
                              if not fields or k in fields])
                objects.append((key[len(self.__redis_prefix):], attrs))
        if objects == []:
            raise NO_SUCH_OBJECT()
        return objects


    @property
    def __redis_prefix(self):
        return 'ldap:'


