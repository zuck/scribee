import string

def foo(x):
    """This is a function."""
    return x + 5

class Test:
    """This is a class.
    
    I think it's a cool class.
    """
    m_x = 0
    
    class Meta:
        """This is an internal empty class.
        
        It's empty and very useless.
        """
        pass
    
    def simpleMethod():
        """This is a class method.
        
        I think it's a cool class method.
        """
        pass
    
    def anotherSimpleMethod(x, y = False):
        """This is another class method.
        
        This is not so cool.
        """
        pass

"""
@entity class_Test__func_simpleMethod

This is a replaced doc.

It's still a simple class method, but with a new doc!
"""
