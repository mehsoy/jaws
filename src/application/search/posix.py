from posix1e import *
from os import stat
import pwd
import grp

'''
 - Represents a posix storage.

 - Inherits from posix1e.ACL via __getattr__ and __iter__, since the 
   posix1e.ACL class is not inheritable.

'''

class UserNotFound(Exception):
    pass

class GroupNotFound(Exception):
    pass

class InvalidACL(Exception):
    pass

class InvalidTagType(Exception):
    pass

class InvalidPermission(Exception):
    pass

class Posix:

    def __init__(self, file):
        self.facl = ACL(file=file)
        self.f = file

    def get_permission(self):
        return str(self.facl)
    
    def put_permission(self, tag_type, name, instruction):
        '''Takes an alphabetic instruction and applies them to the acl entry

        The acl entry is specified by tag_type and name, where tag_name can be
        either `user`, `group` or `other`.

        Warning:
            `name` should be set to `None` when modifying the `other` entry for
            compatibility reasons.
        
        Examples: 
            put_permission(`user`, `bob`, `=rw`)
            put_permission(`user`, `alice`, `-r`)
        '''
        if name and tag_type == 'user':
            func_add = self.add_user_perms
            func_remove = self.remove_user_perms
        elif name and tag_type == 'group':
            func_add = self.add_group_perms
            func_remove = self.remove_group_perms
        elif tag_type == 'other':
            func_add = self.add_other_perms
            func_remove = self.remove_other_perms
        else: 
            raise InvalidTagType

        perms, complement = self.extract_perm_occurrence(instruction)
        if instruction.startswith('+'):
            func_add(name, perms)
        elif instruction.startswith('-'):
            func_remove(name, perms)
        elif instruction.startswith('='):
            func_add(name, perms)
            func_remove(name, complement)
        else:
            raise InvalidPermission
        self.apply()

    def can_modify_acl(self, username):
        return True if username == self.get_owner() else False

    @staticmethod
    def extract_perm_occurrence(string):
        '''
        Searches for occurrences of 'r', 'w' and 'x' in `string` and returns 
        one list `perms` which contains the respective ACL permission enums 
        (e.g. ACL_READ) and another list `complement` containing its complement 
        over all three permissions.
        '''
        perms = set()
        complement = [ACL_READ, ACL_WRITE, ACL_EXECUTE]
        for letter, perm in zip('rwx', complement):
            if letter in string:
                perms.add(perm)
        complement = set(complement) - perms
        return (perms, complement)
            
    def get_perm_of(self, tag_type, name):
        '''Returns the alphabetical acl permission of the requested object.

        `tag_type` can be 'user', 'group' or 'other'.
        '''
        entry = self.find_entry(tag_type, name)
        return str(entry.permset)

    def user_has_perm(self, username, perm):
        '''Returns True, if `username` has `perm` permissions.

        The permission for the user can be provided either by a specific user entry,
        any membership to a group or by the other entry.
        `perm` should be a string representing the alphabetic permission requested
        e.g. 'r', 'w' or 'x'.
        '''
        #Check other entry first, e.g. if file is public
        entry = self.find_entry('other', None)
        if perm in str(entry.permset):
            return True
        #Check if user is in any groups, which have `perm` permissions.
        user_groups = self.get_group_affiliations(username)
        for entry in self:
            if entry.tag_type == ACL_GROUP and entry.qualifier in user_groups:
                if perm in str(entry.permset):
                    return True
        try:
            #Check if user entry exists
            entry = self.find_entry('user', username)
            return perm in str(entry.permset)
        except UserNotFound:
            return False

    def get_group_affiliations(self, username):
        '''Returns a list of ids of groups, which the `username` is a member of

        (This may be very performance heavy. Has to be tested.)
        '''
        groups = [g.gr_gid for g in grp.getgrall() if username in g.gr_mem]
        groups.append(pwd.getpwnam(username).pw_gid)
        return groups

    def find_entry(self, tag_type, name):
        '''Returns the entry with matching `tag_type` and `name`

        If such an entry doesn't exist, a UserNotFound or GroupNotFound exception
        is thrown for tag_types 'user' and 'group' respectively. The other entry
        always exists.
        '''
        if tag_type == 'user':
            return self.find_user_entry(name)
        elif tag_type == 'group':
            return self.find_group_entry(name)
        elif tag_type == 'other':
            return self.find_other_entry()
        else:
            raise InvalidTagType

    def add_user_perms(self, username, perms):
        try:
            entry = self.find_user_entry(username)
        except UserNotFound:
            entry = self.create_entry(ACL_USER, username)
        for perm in perms:
            entry.permset.add(perm)

    def add_group_perms(self, group_name, perms):
        try:
            entry = self.find_group_entry(group_name)
        except GroupNotFound:
            entry = self.create_entry(ACL_GROUP, group_name)
        for perm in perms:
            entry.permset.add(perm)

    def add_other_perms(self, dummy, perms):
        '''
        `dummy` variable for compatibility with add_group_perms
        and add_user_perms. See `self.put_permission`.
        '''
        entry = self.find_other_entry()
        for perm in perms:
            entry.permset.add(perm)

    def remove_user_perms(self, username, perms):
        try:
            entry = self.find_user_entry(username)
        except UserNotFound:
            entry = self.create_entry(ACL_USER, username)
        for perm in perms:
            entry.permset.delete(perm)

    def remove_group_perms(self, group_name, perms):
        try:
            entry = self.find_group_entry(group_name)
        except UserNotFound:
            entry = self.create_entry(ACL_GROUP, group_name)
        for perm in perms:
            entry.permset.delete(perm)

    def remove_other_perms(self, dummy, perms):
        '''
        `dummy` variable for compatibility with remove_group_perms
        and remove_user_perms. See `self.put_permission`.
        '''
        entry = self.find_other_entry()
        for perm in perms:
            entry.permset.delete(perm)
    
    def get_owner(self):
        return pwd.getpwuid(stat(self.f).st_uid).pw_name
        
    def apply(self):
        self.calc_mask()
        if self.valid():
            self.applyto(self.f)
        else: 
            raise InvalidACL
        
    def create_entry(self, tag_type, name):
        if tag_type == ACL_GROUP:
            identifier = self.get_gid(name) 
        elif tag_type == ACL_USER:
            identifier = self.get_uid(name) 
        other_entry = self.find_other_entry()
        entry = self.append()
        entry.copy(other_entry)
        entry.tag_type = tag_type
        entry.qualifier = identifier
        return entry

    def find_user_entry(self, username):
        if username == self.get_owner():
            return self.find_owner_entry()
        uid = self.get_uid(username)
        for entry in self:
            if entry.tag_type == ACL_USER and entry.qualifier == uid:
                return entry
        raise UserNotFound
    
    def find_owner_entry(self):
        for entry in self:
            if entry.tag_type == ACL_USER_OBJ:
                return entry

    def find_group_entry(self, group_name):
        gid = self.get_gid(group_name)
        for entry in self:
            if entry.tag_type == ACL_GROUP and entry.qualifier == gid:
                return entry
        raise GroupNotFound
    
    def find_other_entry(self):
	#Since the `other` entry is at the very bottom of an acl list
	#the list should be traversed in reverse to find it quickly.
        for entry in reversed(list(self)):
            if entry.tag_type == ACL_OTHER:
                return entry
    
    @staticmethod
    def get_uid(username):
        return pwd.getpwnam(username).pw_uid
    
    @staticmethod
    def get_gid(group_name):
        return grp.getgrnam(group_name).gr_gid

    def __getattr__(self, attr):
        try:
            return getattr(self.facl, attr)
        except AttributeError:
            return object.__getattribute__(self, attr)
    
    def __iter__(self):
        for entry in self.facl:
            yield entry

