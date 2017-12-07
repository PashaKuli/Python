### Hash implementation in python
def custom_hash(key):
    """
    Return the hash value of the given key. Uses dbj2
    @param key: String or unicode
    """
    result = 5381
    multiplier = 33

    if isinstance(key, int):
        return key
    
    for char in key:
        result = 33 * result + ord(char)
    return result

class Hash(object):
    def __init__(self, size=8, hashfunction=custom_hash):
        # Total block size which can be array or list
        self._size = 8
        # Initial hashtable size
        self.__initial_size = self._size
        # Counter for holding total used slots
        self._used_slots = 0
        # Counter for holding deleted keys
        self._dummy_slots = 0
        # Holds all the keys
        self._keys = [None] * self._size
        # Holds all the values
        self._values = [None] * self._size
        # Alias for custom_hash function
        self.hash = custom_hash
        # threshold is used for increasing hash table
        self._max_threshold = 0.70
    
    def should_expand(self):
        """Returns True or False
        
        If used slots and dummy slots are more than 70% resize the hash table.
        """
        return (float(self._used_slots + self._dummy_slots) / self._size) >= self._max_threshold

    def _probing(self, current_position):
        """Quadratic probing to get new position when collision occurs.
        @param current_position: position at already element is present.
        """
        # Algorithm is copied from CPython http://hg.python.org/cpython/file/52f68c95e025/Objects/dictobject.c#l69
        return ((5 + current_position) + 1) % self._size
    
    def _set_item_at_pos(self, position, key, value):
        self._keys[position] = key
        self._values[position] = value
        
        self._used_slots += 1
        
    def _set_item(self, position, key, value):
        """sets key and value in the given position.
        If position has already value in it, calls _probing to get next position
        @param position: index
        @param key: key
        @param value: value
        """
        existing_key = self._keys[position]
        
        if existing_key is None or existing_key == key:
            # Empty or update
            self._set_item_at_pos(position, key, value)
        else:
            # Collision needs a probing. This needs to be recursive.
            new_position = self._probing(position)
            self._set_item(new_position, key, value)
        
    def _reposition(self, keys, values):
        """Reposition all the keys and values.
        This is called whenever load factor or threshold has crossed the limit.
        """
        for (key, value) in zip(keys, values):
            if key is not None:
                hashvalue = self.hash(key)
                position = self._calculate_position(hashvalue)
                
                self._set_item(position, key, value)
       
    def _resize(self):
        old_keys = self._keys
        old_values = self._values
        
        # New size
        self._size = self._size * 4
        
        # create new block of memory and clean up old keys positions
        self._keys = [None] * self._size
        self._values = [None] * self._size
        self._used_slots = 0
        self._dummy_slots = 0
        
        # Now reposition the keys and values
        
        self._reposition(old_keys, old_values)
        
    def _calculate_position(self, hashvalue):
        return hashvalue % self._size
        
    def raise_if_not_acceptable_key(self, key):
        if not isinstance(key, (basestring, int)):
            raise TypeError("Key should be int or string or unicode")
        
    def put(self, key, value):
        """Given a key and value add to the hashtable.
        Key should be int or string or unicode.
        """
        self.raise_if_not_acceptable_key(key)
        
        if self.should_expand():
            self._resize()
            
        position = self._calculate_position(self.hash(key))
        self._set_item(position, key, value)
        
    def _get_pos_recursively(self, position, key):
        new_position = self._probing(position)
        tmp_key = self._keys[new_position]
        
        if tmp_key == None:
            # At new position the key is empty raise ane exception
            raise KeyError(u"{} key not found".format(key))
        elif tmp_key != key:
            # Again check for next position
            return self._get_pos_recursively(new_position, key)
        else:
            return new_position
        
    def _get_pos(self, key):
        """
        Returns position of the key
        """
        self.raise_if_not_acceptable_key(key)
        position = self._calculate_position(self.hash(key))
        
        tmp_key = self._keys[position]

        if tmp_key == None:
            raise KeyError("{} doesn't exist".format(key))
            
        elif tmp_key != key:
            # Probably collision and get next position using probing
            return self._get_pos_recursively(position, key) 
        else:
            return position
        
    def get(self, key):
        position = self._get_pos(key)

        if position is None:
            return None
        
        return self._values[position]
    
    def _delete_item(self, position, key):
        self._keys[position] = None
        self._values[position] = None
        
        self._dummy_slots += 1
        
    def delete(self, key):
        """Deletes the key if present. KeyError is raised if Key is missing.
        """
        position = self._get_pos(key)
        
        if position is None:
            raise KeyError(key)
            
        self._delete_item(position, key)
        
