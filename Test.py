__author__ = 'ian'


# 'ALTERNATIVE_PAIRED'
#
# class Switch(object):
#
#     def __init__(self, value):
#         self.value = value
#         self.switch()
#
#
#     def switch(self):
#         return {
#             'ALTERNATIVE': self.alt(),
#             'ALTERNATIVE_PAIRED': self.alt_paired(),
#             'ALTERNATIVE_PARENT': self.alt_parent(),
#             'ALTERNATIVE_MIXED_PAIRED': self.mixed_paired()
#         }[self.value]() #.get(self.value)
#
#     def alt(self):
#         print("doing alt up")
#
#     def alt_paired(self):
#         print("alt paired here")
#
#     def alt_parent(self):
#         print("fear your parents")
#
#     def mixed_paired(self):
#         print("mixed pairings")
#
#
#
# values = ['ALTERNATIVE','ALTERNATIVE_PAIRED','ALTERNATIVE_PARENT','ALTERNATIVE_MIXED_PAIRED']
# for val in values:
#     dummy = Switch(val)

# class switch(object):
#     def __init__(self, value):
#         self.value = value
#         self.fall = False
#
#     def __iter__(self):
#         """Return the match method once, then stop"""
#         yield self.match
#         raise StopIteration
#
#     def match(self, *args):
#         """Indicate whether or not to enter a case suite"""
#         if self.fall or not args:
#             return True
#         elif self.value in args: # changed for v1.5, see below
#             self.fall = True
#             return True
#         else:
#             return False
#
# import string
# c = 'A'
# for case in switch(c):
#     if case(*string.lowercase): # note the * for unpacking as arguments
#         print "c is lowercase!"
#         break
#     if case(*string.uppercase):
#         print "c is uppercase!"
#         break
#     if case('!', '?', '.'): # normal argument passing style also applies
#         print "c is a sentence terminator!"
#         break
#     if case(): # default
#         print "I dunno what c was!"

# class switch(object):
#     def __init__(self, value):
#         self.value = value
#         self.fall = False
#
#     def __iter__(self):
#         """Return the match method once, then stop"""
#         yield self.match
#         raise StopIteration
#
#     def match(self, *args):
#         """Indicate whether or not to enter a case suite"""
#         if self.fall or not args:
#             return True
#         elif self.value in args: # changed for v1.5, see below
#             self.fall = True
#             return True
#         else:
#             return False

class switch(object):
    def __init__(self, value):
        self.value = value
        #self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            return True
        else:
            return False
# The following example is pretty much the exact use-case of a dictionary,
# but is included for its simplicity. Note that you can include statements
# in each suite.
v = 'ten'
for case in switch(v):
    if case('one'):
        print 1
        break
    if case('two'):
        print 2
        break
    if case('ten'):
        print 10
        break
    if case('eleven'):
        print 11
        break
    if case(): # default, could also just omit condition or 'if True'
        print "something else!"
        # No need to break here, it'll stop anyway